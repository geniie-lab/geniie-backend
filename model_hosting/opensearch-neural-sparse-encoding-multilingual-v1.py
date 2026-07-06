import sys
import json
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForMaskedLM
from huggingface_hub import hf_hub_download

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"INFO:\tUsing device: {device}", file=sys.stderr)

MODEL_NAME = "opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME).to(device)
model.eval()

print(f"INFO:\tModel max length: {tokenizer.model_max_length}", file=sys.stderr)

# Vocab ids of the special tokens ([CLS], [SEP], [PAD], [UNK], [MASK]). SPLADE
# max-pooling otherwise assigns these real weight in the output vector (esp.
# [MASK]), leaking meaningless high-weight terms into the index. The reference
# encoder zeroes them (`values[:, special_token_ids] = 0`); we mirror that.
special_token_ids = [tokenizer.vocab[t] for t in tokenizer.special_tokens_map.values()]

# Query-side IDF table. This is a "doc-only" neural-sparse model: passages run
# through the full MLM (learned term expansion), but QUERIES are encoded WITHOUT
# a model forward -- each query token simply carries its precomputed inverse
# document frequency (see /embed/query and the model card). Load the author-
# provided idf.json ({token: weight}) once at startup.
_idf_path = hf_hub_download(repo_id=MODEL_NAME, filename="idf.json")
with open(_idf_path) as f:
    token_idf = json.load(f)
print(f"INFO:\tLoaded IDF table with {len(token_idf)} tokens", file=sys.stderr)


class PredictRequest(BaseModel):
    input: list[str]
class DecodeRequest(BaseModel):
    token_ids: list[int]

app = FastAPI(title=MODEL_NAME)

# Counter used to periodically return cached allocator blocks (see _encode_documents).
_predict_calls = 0


def _encode_documents(texts: list[str]) -> list[dict]:
    """
    Document/passage encoding: full MLM forward + SPLADE pooling, returning
    sparse {token: weight} maps for OpenSearch neural sparse indexing.
    """
    global _predict_calls

    with torch.no_grad():
        encoded = tokenizer(
            texts,
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

        # Drop the special tokens ([CLS]/[SEP]/[MASK]/...) from the doc vector so
        # they never surface as terms; mirrors the reference get_sparse_vector.
        values[:, special_token_ids] = 0

        # Free the big [batch, seq, vocab] tensor before extraction.
        del logits, encoded

    # Vectorised extraction: only touch the nonzero vocab ids (a few hundred per
    # text) instead of looping over the full ~250k vocabulary in Python.
    results = []
    for row in values:
        idx = torch.nonzero(row > 0, as_tuple=False).squeeze(1)
        tokens = tokenizer.convert_ids_to_tokens(idx.tolist())
        weights = row[idx].tolist()

        sparse = {}
        for token, weight in zip(tokens, weights):
            # Drop tokens that are not representable as UTF-8 (pieces holding
            # lone surrogates from byte-level decoding). Downstream JSON layers
            # normalize each of them to the same U+FFFD string, so distinct
            # tokens collide into duplicate object keys that OpenSearch rejects.
            try:
                token.encode("utf-8")
            except UnicodeEncodeError:
                continue
            if weight > sparse.get(token, 0.0):
                sparse[token] = weight

        results.append(sparse)

    # Periodically hand cached allocator blocks back to the (unified) memory pool
    # so RSS doesn't creep. Periodic, not every call, to avoid per-request sync.
    _predict_calls += 1
    if device == "cuda" and _predict_calls % 50 == 0:
        torch.cuda.empty_cache()

    return results


def _encode_query(texts: list[str]) -> list[dict]:
    """
    Query encoding for this doc-only model: NO model forward. Each unique
    (non-special) query token is weighted by its IDF, per the model card.
    Output format matches _encode_documents ({token: weight}) so it drives
    OpenSearch neural_sparse queries directly.
    """
    results = []
    for text in texts:
        ids = tokenizer.encode(text, add_special_tokens=False)
        sparse = {}
        for token in tokenizer.convert_ids_to_tokens(ids):
            weight = token_idf.get(token)
            if weight is None:  # out-of-vocab / no IDF entry (incl. special tokens)
                continue
            try:
                token.encode("utf-8")
            except UnicodeEncodeError:
                continue
            # Presence-based (like the reference one-hot * idf): duplicate query
            # tokens collapse to a single IDF weight.
            sparse[token] = weight
        results.append(sparse)
    return results


@app.post("/embed/passages")
async def embed_passages(req: PredictRequest):
    return _encode_documents(req.input)


@app.post("/embed/query")
async def embed_query(req: PredictRequest):
    return _encode_query(req.input)


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
