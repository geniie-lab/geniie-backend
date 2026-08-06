# Model Hosting

Host a machine learning model in an external server with GPU.

```bash
sudo apt install uvicorn
```

## Port map

One port per model; **8000 is reserved for vLLM**. This map must stay in sync
with `indexing/opensearch/ml_model_registration.ipynb` (`PORTS`), which
registers the models in OpenSearch via `host.docker.internal:<port>`.

| Port | Model | Script |
| --- | --- | --- |
| 8001 | [intfloat/multilingual-e5-large](multilingual-e5-large.py) — multilingual dense | `multilingual-e5-large.py` |
| 8002 | [opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1](opensearch-neural-sparse-encoding-multilingual-v1.py) — multilingual sparse, doc-only query side | `opensearch-neural-sparse-encoding-multilingual-v1.py` |
| 8003 | [intfloat/e5-large-v2](e5-large-v2.py) — English dense (MS MARCO / TREC DL) | `e5-large-v2.py` |
| 8004 | [naver/splade-v3](splade-v3.py) — English sparse, symmetric (MS MARCO / TREC DL; gated repo, CC BY-NC-SA 4.0) | `splade-v3.py` |

Launch commands:

```bash
python -m uvicorn multilingual-e5-large:app --host 0.0.0.0 --port 8001
python -m uvicorn opensearch-neural-sparse-encoding-multilingual-v1:app --host 0.0.0.0 --port 8002
python -m uvicorn e5-large-v2:app --host 0.0.0.0 --port 8003
python -m uvicorn splade-v3:app --host 0.0.0.0 --port 8004
```

- Visit http://localhost:800N/docs to check available methods and test
- These are plain uvicorn processes: they do not survive a reboot. Restart
  them before any indexing/search work (OpenSearch model IDs stay valid; the
  servers just need to be listening again).
