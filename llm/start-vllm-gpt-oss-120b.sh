#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-gpt-oss-120b \
  --ipc=host \
  -p 127.0.0.1:8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.03-py3 \
  vllm serve openai/gpt-oss-120b \
  --host 0.0.0.0 \
  --no-enable-prefix-caching \
  --gpu-memory-utilization 0.7 \
  --kv-cache-memory-bytes 17179869184 \
  --max-model-len 65536 \
  --max-num-seqs 4
  
