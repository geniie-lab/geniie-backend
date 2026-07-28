#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-nemotron3-super-120b-tools \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.06-py3 \
  vllm serve nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4 \
  --enable-auto-tool-choice \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --kv-cache-memory-bytes 17179869184 \
  --max-model-len 131072 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching \
  --reasoning-parser nemotron_v3 \
  --tool-call-parser qwen3_coder
