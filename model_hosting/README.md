# Model Hosting

Host a machine learning model in an external server with GPU.

```bash
sudo apt install uvicorn
```
```bash
python -m uvicorn [filename]:app --host 0.0.0.0 --port 8000
```

- Then visit http://localhost:8000/docs to check available methods and test
- Change port number if you plan to host multiple models simultaneously

Model scripts

- [intfloat/multilingual-e5-large](multilingual-e5-large.py)
- [intfloat/e5-large-v2](e5-large-v2.py) — English dense encoder for MS MARCO / TREC DL
- [naver/splade-v3](splade-v3.py) — English learned-sparse encoder for MS MARCO / TREC DL
- [opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1](opensearch-neural-sparse-encoding-multilingual-v1.py)