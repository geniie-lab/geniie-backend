#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-qwen3-80b \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.06-py3 \
  vllm serve nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4 \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --kv-cache-memory-bytes 17179869184 \
  --max-model-len 131072 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching
