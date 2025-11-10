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
---

### <0001f9e9> OpenAPI Schema (Cloud Run / Natacha API)

**Servicio:** `natacha-api`
**Proyecto:** `asistente-sebastian`
**Región:** `us-central1`
**Revisión activa:** `natacha-api-00422-qcw`
**URL público:** [https://natacha-api-422255208682.us-central1.run.app](https://natacha-api-422255208682.us-central1.run.app)

#### 📘 Endpoint de esquema (para Actions / herramientas externas)
- JSON: `https://natacha-api-422255208682.us-central1.run.app/openapi.v1.json`

#### <0001f9f1> Estructura técnica
- **Base module serving:** `entrypoint_app.py`
- **Router responsable:** `routes/openapi_compat.py`
- **Versión de OpenAPI publicada:** `3.1.0`
- **Servers:** `[{ "url": "https://natacha-api-422255208682.us-central1.run.app" }]`
- **Env var usada:** `OPENAPI_PUBLIC_URL`
- **Propósito:** Publicar un esquema OpenAPI compatible con Actions y otras integraciones externas.

#### 🛠 Cómo actualizar solo la versión del esquema
1. Editar `routes/openapi_compat.py` y ajustar: `schema["openapi"] = "3.1.0"` (o `"3.1.1"` si tu editor lo exige).
2. Build & deploy normales del servicio.
3. Verificar: `curl -fsS "https://natacha-api-422255208682.us-central1.run.app/openapi.v1.json" | jq '.openapi, .servers'`
