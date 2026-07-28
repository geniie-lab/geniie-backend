#!/bin/bash

docker run -d \
  --runtime nvidia \
  --gpus all \
  --name vllm-mistral-8b \
  --ipc host \
  -p 8000:8000 \
  --restart unless-stopped \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:26.06-py3 \
  vllm serve mistralai/Ministral-8B-Instruct-2410 \
  --config-format mistral \
  --enable-auto-tool-choice \
  --gpu-memory-utilization 0.7 \
  --host 0.0.0.0 \
  --load-format mistral \
  --max-model-len 32768 \
  --max-num-seqs 1 \
  --no-enable-prefix-caching \
  --tokenizer-mode mistral \
  --tool-call-parser mistral
