import sys
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"INFO:\tUsing device: {device}", file=sys.stderr)

MODEL_NAME = "intfloat/multilingual-e5-large"
model = SentenceTransformer(MODEL_NAME, device=device)
model.eval()
tokenizer = model.tokenizer

print(f"INFO:\tModel max length: {tokenizer.model_max_length}", file=sys.stderr)


class PredictRequest(BaseModel):
    input: list[str]
class DecodeRequest(BaseModel):
    token_ids: list[int]

app = FastAPI(title=MODEL_NAME)

# Counter used to periodically return cached allocator blocks (unified memory).
_encode_calls = 0


def _encode(texts: list[str]) -> list[list[float]]:
    """
    Encode texts to normalized dense vectors.

    The heavy transformer matmuls run in bf16 on the tensor cores (~1.5-2x on
    Blackwell); embeddings are returned as fp32 lists. Cached allocator blocks
    are periodically released so RSS stays flat on unified memory.
    """
    global _encode_calls

    with torch.no_grad(), torch.autocast(device_type=device, dtype=torch.bfloat16):
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_tensor=True,
        )

    result = embeddings.float().cpu().tolist()

    _encode_calls += 1
    if device == "cuda" and _encode_calls % 50 == 0:
        torch.cuda.empty_cache()

    return result


@app.post("/embed/passages")
async def embed_passages(req: PredictRequest):
    return _encode([f"passage: {t}" for t in req.input])


@app.post("/embed/query")
async def embed_query(req: PredictRequest):
    return _encode([f"query: {t}" for t in req.input])


@app.post("/tokenize")
async def tokenize(req: PredictRequest):
    return [
        {
            "text": text,
            "tokens": tokenizer.convert_ids_to_tokens(
                tokenizer.encode(
                    text,
                    add_special_tokens=False
                )
            ),
            "token_ids": tokenizer.encode(
                text,
                add_special_tokens=False
            ),
            "token_count": len(
                tokenizer.encode(
                    text,
                    add_special_tokens=False
                )
            ),
        }
        for text in req.input
    ]


@app.post("/decode")
async def decode(req: DecodeRequest):
    return {
        "text": tokenizer.decode(req.token_ids)
    }


@app.get("/health")
async def health():
    return {"status": "ok"}