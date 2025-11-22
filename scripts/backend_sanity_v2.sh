#!/usr/bin/env bash
set -e

BASE="https://natacha-api-422255208682.us-central1.run.app"

echo "== Health =="
curl -s "$BASE/health" | jq .
echo

echo "== Memory v2: info =="
curl -s "$BASE/memory/v2/ops/memory-info" | jq .
echo

echo "== Memory v2: store sample =="
curl -s -X POST "$BASE/memory/v2/store" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "text": "Sanity memory v2 desde backend_sanity_v2",
        "tags": ["sanity", "backend"]
      }
    ]
  }' | jq .
echo

echo "== Memory v2: search =="
curl -s -X POST "$BASE/memory/v2/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "backend_sanity_v2",
    "top_k": 5,
    "use_semantic": true
  }' | jq .
echo

echo "== Tasks v1: add =="
curl -s -X POST "$BASE/v1/tasks/add" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "LLVC",
    "title": "Sanity task v1",
    "detail": "Tarea desde backend_sanity_v2",
    "due": "2025-11-22T12:00:00"
  }' | jq .
echo

echo "== Tasks v1: search =="
curl -s -X POST "$BASE/v1/tasks/search" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "LLVC",
    "limit": 5
  }' | jq .
echo
