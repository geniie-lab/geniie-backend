#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-gpt-oss-120b \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.03-py3 \
  vllm serve openai/gpt-oss-120b \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --kv-cache-memory-bytes 17179869184 \
  --max-model-len 131072 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching \
  --reasoning-parser openai_gptoss
