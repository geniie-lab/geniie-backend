import sys
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"INFO:\tUsing device: {device}", file=sys.stderr)

# Multilingual cross-encoder reranker (100+ languages, Apache-2.0). Scores
# (query, passage) pairs jointly; used as the second stage over BM25/DPR/SPLADE
# candidates for both the English (MS MARCO / TREC DL) and Japanese (NTCIR)
# tracks. Public repo -- downloads to the HF cache on first launch (~2.3 GB).
MODEL_NAME = "BAAI/bge-reranker-v2-m3"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
model.eval()

# Pairs are truncated to this many tokens (query + passage combined). The
# backbone accepts up to 8192, but reranking quality saturates well below
# that and latency grows quadratically with length.
MAX_LENGTH = 1024
# Pairs per forward pass; keeps memory bounded for large candidate lists.
BATCH_SIZE = 32

print(f"INFO:\tMax pair length: {MAX_LENGTH}", file=sys.stderr)


class RerankRequest(BaseModel):
    query: str
    texts: list[str]
class CohereRerankRequest(BaseModel):
    query: str
    documents: list[str]
    top_n: int | None = None

app = FastAPI(title=MODEL_NAME)

# Counter used to periodically return cached allocator blocks (unified memory).
_rerank_calls = 0


def _score_pairs(query: str, texts: list[str]) -> list[float]:
    """
    Score (query, text) pairs with the cross-encoder. Returns one raw
    relevance logit per text (higher = more relevant); OpenSearch's rerank
    processor sorts by these directly, so no sigmoid is applied.
    """
    global _rerank_calls

    scores: list[float] = []
    with torch.no_grad():
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            encoded = tokenizer(
                [query] * len(batch),
                batch,
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                pad_to_multiple_of=8,
                return_tensors="pt",
            ).to(device)

            # Run the transformer in bf16 on the tensor cores (~1.5-2x on
            # Blackwell); logits are returned as fp32 floats.
            with torch.autocast(device_type=device, dtype=torch.bfloat16):
                logits = model(**encoded).logits  # [batch, 1]

            scores.extend(logits.squeeze(-1).float().cpu().tolist())
            del encoded, logits

    _rerank_calls += 1
    if device == "cuda" and _rerank_calls % 50 == 0:
        torch.cuda.empty_cache()

    return scores


@app.post("/rerank")
async def rerank(req: RerankRequest):
    """
    Score req.texts against req.query. Returns {"scores": [...]} in input
    order -- the caller (OpenSearch rerank processor or a notebook) re-sorts.
    """
    return {"scores": _score_pairs(req.query, req.texts)}


@app.post("/v1/rerank")
async def rerank_cohere(req: CohereRerankRequest):
    """
    Cohere-Rerank-compatible endpoint, so the OpenSearch connector can use the
    built-in connector.pre_process.cohere.rerank / post_process.cohere.rerank
    functions (no custom painless scripts). Returns results sorted by score
    descending, each carrying the document's original index.
    """
    scores = _score_pairs(req.query, req.documents)
    order = sorted(range(len(scores)), key=lambda i: -scores[i])
    if req.top_n:
        order = order[:req.top_n]
    return {"results": [
        {"index": i, "relevance_score": scores[i]} for i in order
    ]}


@app.get("/health")
async def health():
    return {"status": "ok"}
