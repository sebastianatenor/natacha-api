# Natacha API — Stable State v1.0.1

## Runtime
- Platform: Google Cloud Run
- Region: us-central1
- Python: 3.10 (production), 3.11 (local/dev allowed)
- Framework: FastAPI
- Server: Uvicorn

## Cognitive Systems
- Memory: NDJSON canonical store
  - Path: /tmp/memory_store.jsonl (Cloud Run)
  - Local fallback: ./memory_store.jsonl
- Semantic: heuristic engine (default)
  - Embeddings: optional, lazy-load, disabled by default
- Guardrails: pre-ML unified guardrail (always-on)
- Checkpoints: revision-bound, restore-safe, non-blocking

## Guarantees (Non-Negotiable)
- Cold start safe
- Deterministic startup (no hidden side effects)
- Canonical memory path
- Guardrail-first execution
- Restore process never blocks startup
- No autonomous actions without explicit enablement

## Stable Endpoints (Gateway Contract)
These endpoints are **public, stable and backward-compatible**.

- GET  /health
- POST /agent/interact
- GET  /get_system_state
- GET  /system/executive/state
- GET  /system/guardrail/check
- GET  /system/restore/status

Any endpoint not listed here is considered:
- internal
- experimental
- or legacy

## Stability Rules
- Core endpoint signatures must not change
- Cognitive logic must remain side-effect free
- Memory writes must be explicit and traceable
- Semantic or vector engines must be opt-in
- New capabilities must be isolated by design

## Deployment Rules
- Single deploy unit (no partial deploys)
- One revision = one cognitive state
- Rollback must be stateless-safe
- Memory persistence must survive restarts

## Tag
- v1.0.1-stable
