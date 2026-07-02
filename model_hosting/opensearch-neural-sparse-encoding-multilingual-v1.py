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
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device)
model.eval()

print(f"INFO:\tModel max length: {tokenizer.model_max_length}", file=sys.stderr)

class PredictRequest(BaseModel):
    input: list[str]
class DecodeRequest(BaseModel):
    token_ids: list[int]

app = FastAPI(title=MODEL_NAME)

# Counter used to periodically return cached allocator blocks (see /predict).
_predict_calls = 0


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
            truncation=True,          # guard only the model's own max length; chunk-length policy is the caller's
            pad_to_multiple_of=8,     # bucket seq lengths -> far fewer distinct tensor shapes (masked out)
            return_tensors="pt",
        ).to(device)

        # Run the heavy vocab projection in bf16 on the tensor cores (~1.5-2x on
        # Blackwell).
        with torch.autocast(device_type=device, dtype=torch.bfloat16):
            logits = model(**encoded).logits  # [batch, seq, vocab] (bf16)

        # SPLADE doc weighting: log1p(relu(x)) is monotonic, so it commutes with
        # the max-pool. Max-pool the raw bf16 logits FIRST (in place -inf mask on
        # padding), then apply the transform to the small [batch, vocab] result.
        # This avoids materialising any full-size fp32 copy: peak memory is the
        # bf16 logits alone (a long-doc batch previously spiked ~5x that).
        logits.masked_fill_(
            (encoded["attention_mask"] == 0).unsqueeze(-1), float("-inf")
        )
        values = torch.log1p(torch.relu(logits.max(dim=1).values.float()))

        # Free the big [batch, seq, vocab] tensor before extraction.
        del logits, encoded

    # Vectorised extraction: only touch the nonzero vocab ids (a few hundred per
    # text) instead of looping over the full ~250k vocabulary in Python.
    results = []
    for row in values:
        idx = torch.nonzero(row > 0, as_tuple=False).squeeze(1)
        tokens = tokenizer.convert_ids_to_tokens(idx.tolist())
        weights = row[idx].tolist()
        results.append(dict(zip(tokens, weights)))

    # Periodically hand cached allocator blocks back to the (unified) memory pool
    # so RSS doesn't creep. Periodic, not every call, to avoid per-request sync.
    global _predict_calls
    _predict_calls += 1
    if device == "cuda" and _predict_calls % 50 == 0:
        torch.cuda.empty_cache()

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