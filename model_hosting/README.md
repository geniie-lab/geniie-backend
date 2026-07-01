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
- [opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1](opensearch-neural-sparse-encoding-multilingual-v1.py)
- [intfloat/multilingual-e5-large](multilingual-e5-large.py)