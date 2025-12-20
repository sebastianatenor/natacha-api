# Natacha API — Stable State v1.0.0

## Runtime
- Platform: Google Cloud Run
- Region: us-central1
- Python: 3.10
- FastAPI

## Cognitive Systems
- Memory: NDJSON canonical (/tmp/memory_store.jsonl)
- Semantic: SentenceTransformers (lazy-load)
- Checkpoints: self_checkpoint (revision-bound)

## Guarantees
- Cold start safe
- Deterministic startup
- Canonical memory path
- Force checkpoint endpoint

## Stable Endpoints
- /ops/system/state
- /ops/system/full_status
- /ops/system/last_checkpoint
- /ops/system/force_checkpoint
- /ops/semantic/analyze

## Tag
- v1.0.0-stable
