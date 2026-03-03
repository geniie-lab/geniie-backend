# LLM Integration

## Remote Access

- OpenAI: [https://openai.com/api/](https://openai.com/api/)
- Google: [https://ai.google.dev/gemini-api/](https://ai.google.dev/gemini-api/)
- OpenRouter: [https://openrouter.ai/](https://openrouter.ai/)
- Groq: [https://groq.com/](https://groq.com/)
- Many more ...


## Local Access

### Ollama

Model: `llama3.3:70b-instruct-q4_K_M`

```bash
docker run -d \
  --runtime nvidia \
  --gpus all \
  --name ollama \
  -p 11343:11343 \
  -v ~/.ollama:/root/.ollama \
  ollama/ollama:latest
```

```bash
docker exec -it ollama pull llama3.3:70b-instruct-q4_K_M
```

Connection Test

```bash
curl http://localhost:11434/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama3.3:70b-instruct-q4_K_M",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
    }' | jq
```

### vLLM

Model: `nvidia/Llama-3.3-70B-Instruct-NVFP4`

```bash
docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-llama3.3-70b \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.01-py3 vllm serve \
  --model nvidia/Llama-3.3-70B-Instruct-NVFP4 \
  --no-enable-prefix-caching \
  --gpu-memory-utilization 0.75
```

Connection Test

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "nvidia/Llama-3.3-70B-Instruct-NVFP4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
    }' | jq
```