import sys
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"INFO:\tUsing device: {device}", file=sys.stderr)

MODEL_NAME = "intfloat/multilingual-e5-large"
model = SentenceTransformer(MODEL_NAME, device=device,)
tokenizer = model.tokenizer

class PredictRequest(BaseModel):
    input: list[str]
class DecodeRequest(BaseModel):
    token_ids: list[int]

app = FastAPI(title=MODEL_NAME)
@app.post("/embed/passages")
async def embed_passages(req: PredictRequest):
    embeddings = model.encode(
        [f"passage: {t}" for t in req.input],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()


@app.post("/embed/query")
async def embed_query(req: PredictRequest):
    embeddings = model.encode(
        [f"query: {t}" for t in req.input],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()


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