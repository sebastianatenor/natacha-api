#!/bin/sh
set -e

MEMORY_PATH="/tmp/memory_store.jsonl"
GCS_PATH="gs://natacha-memory-store/memory_store.jsonl"

if [ ! -f "$MEMORY_PATH" ]; then
  echo "[BOOTSTRAP] Downloading memory store from GCS..."
  gsutil cp "$GCS_PATH" "$MEMORY_PATH"
  echo "[BOOTSTRAP] Memory store ready"
else
  echo "[BOOTSTRAP] Memory store already present"
fi
