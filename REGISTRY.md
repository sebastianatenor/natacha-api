---

## Canonical API (Core Contract)

**Project:** `asistente-sebastian`  
**Stable Revision:** `natacha-api-00422-qcw`
**Runtime URL:** https://natacha-api-mkwskljrhq-uc.a.run.app
**Legacy Runtime URL:** https://natacha-api-422255208682.us-central1.run.app
**Last Verified:** 2025-11-10

### ✅ Canonical Endpoints
| Path | Purpose | Contract Status |
|------|---------|-----------------|
| `/health` | Basic heartbeat | Stable |
| `/health/deps` | Dependency status (firestore, env) | Stable |
| `/health/debug_source` | Returns runtime path & SHA256 | Stable |
| `/ops/summary` | Aggregated operational summary | Stable |
| `/ops/insights` | Operational metrics insights | Stable |

### 🔒 Invariants
1. **Status Codes:**
   - 2xx in normal flow.
   - 4xx for bad input.
   - Never 5xx for optional dependency failures — those must degrade gracefully.
2. **Format:**
   - JSON, ISO-8601 timestamps, predictable keys (`generated_at`, `deps`, `status`).
3. **Idempotent GETs:**
   - All GET routes are read-only and side-effect-free.
4. **Safe Flags (no contract changes):**
   - `SAFE_MODE=1`
   - `OPS_DISABLE_FIRESTORE=1`
   - `OPS_FORCE_BACKEND=gcs`

### 🧩 Evolution Policy
- `/health*` y `/ops*` son **canónicas** — deben permanecer retro-compatibles.
- Nuevas APIs o cambios estructurales van bajo `/v1/...`.
- Deprecations con dual-publish (old + new) por al menos 2 revisiones antes de remover.

### 🧠 Observability
- Log fields: `route`, `rev`, `flags`, `severity`.
- Alert rules por revisión:
  - Error rate ≥1% (5xx)
  - Latency P95 deviation ≥20% from baseline

### 📜 CI Smoke Definition
Ejecutado durante Cloud Build:
```bash
curl -sf https://${HOST}/health
curl -sf https://${HOST}/ops/summary?limit=1
eof