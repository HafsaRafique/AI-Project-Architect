#!/usr/bin/env bash
# Pulls the free, open-source models PixelRAG needs into the running Ollama
# container. Run this once after `docker compose up -d`.
set -euo pipefail

echo "Waiting for Ollama to be ready..."
until curl -sf http://localhost:11434/api/tags > /dev/null; do
  sleep 2
done

echo "Pulling vision model (qwen2.5vl:7b) — this is several GB, be patient..."
docker exec pixelrag-ollama ollama pull qwen2.5vl:7b

echo "Pulling text model (qwen2.5:7b)..."
docker exec pixelrag-ollama ollama pull qwen2.5:7b

echo "Pulling embedding model (nomic-embed-text)..."
docker exec pixelrag-ollama ollama pull nomic-embed-text

echo "All models pulled. PixelRAG backend is ready at http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
