import sys
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"INFO:\tUsing device: {device}", file=sys.stderr)

MODEL_NAME = "opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)
model.eval()

class PredictRequest(BaseModel):
    input: list[str]
class DecodeRequest(BaseModel):
    token_ids: list[int]

app = FastAPI(title=MODEL_NAME)
@app.post("/predict")
async def predict(req: PredictRequest):
    """
    Returns sparse token-weight maps suitable for
    OpenSearch neural sparse indexing.
    """

    with torch.no_grad():
        encoded = tokenizer(
            req.input,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        logits = model(**encoded).logits

        values, _ = torch.max(
            torch.log1p(torch.relu(logits)),
            dim=1,
        )

        attention_mask = encoded["attention_mask"]
        results = []

        for batch_idx in range(values.shape[0]):
            sparse = {}

            token_ids = encoded["input_ids"][batch_idx]
            weights = values[batch_idx]

            for vocab_id, weight in enumerate(weights):
                score = float(weight)

                if score <= 0:
                    continue

                token = tokenizer.convert_ids_to_tokens(vocab_id)
                sparse[token] = score

            results.append(sparse)

    return results


@app.post("/tokenize")
async def tokenize(req: PredictRequest):
    return [
        {
            "text": text,
            "token_ids": tokenizer.encode(
                text,
                add_special_tokens=False,
            ),
            "token_count": len(
                tokenizer.encode(
                    text,
                    add_special_tokens=False,
                )
            ),
            "tokens": tokenizer.convert_ids_to_tokens(
                tokenizer.encode(
                    text,
                    add_special_tokens=False,
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