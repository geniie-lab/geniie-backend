#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-gemma4-26b \
  --ipc=host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:gemma4-cu130 \
  --model nvidia/Gemma-4-26B-A4B-NVFP4 \
  --host 0.0.0.0 \
  --quantization modelopt \
  --moe-backend marlin \
  --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.7 \
  --kv-cache-memory-bytes 17179869184 \
  --max-model-len 131072 \
  --max-num-seqs 4 \
  --reasoning-parser gemma4 \
  --tool-call-parser gemma4 \
  --enable-auto-tool-choice \
  --trust-remote-code