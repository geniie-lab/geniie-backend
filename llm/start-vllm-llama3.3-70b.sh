#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-llama3.3-70b \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.06-py3 \
  vllm serve nvidia/Llama-3.3-70B-Instruct-NVFP4 \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --kv-cache-memory-bytes 25769803776 \
  --max-model-len 131072 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching
