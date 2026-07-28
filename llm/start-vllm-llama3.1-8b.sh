#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-llama3.1-8b \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.06-py3 \
  vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --enable-auto-tool-choice \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching \
  --tool-call-parser llama3_json
