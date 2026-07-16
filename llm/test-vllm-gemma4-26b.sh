#!/bin/bash

curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "nvidia/Gemma-4-26B-A4B-NVFP4",
        "messages": [
            {"role": "system", "content": "You are an expert software engineer. When asked to write code, provide the clean, optimized, fully-functional code or explanation. Ensure code blocks are clearly formatted with Markdown."},
            {"role": "user", "content": "Write a Python function that takes a string of words and returns the longest word. If there are multiple, return the shortest among them. If the string is empty or contains only spaces, return None."}
        ]
    }' | jq
