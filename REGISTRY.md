# Natacha API - Registry
- URL: https://natacha-api-422255208682.us-central1.run.app
- Revisión: natacha-api-00428-g49
- Service Account: natacha-firestore-access@asistente-sebastian.iam.gserviceaccount.com
- Secret montado: natacha-firestore-key

## 2025-11-13 – Estado estable Natacha API

- Revisión Cloud Run: natacha-api-00484-drq
- Imagen: gcr.io/asistente-sebastian/natacha-api:natacha-v1
- Health: /health → OK
- Memoria:
  - /memory/engine/recent
  - /memory/engine/context_bundle
  - summary y system_rule funcionando para user_id=sebastian
- Tasks:
  - /tasks/add – crea bien tareas (sin error "values must be non-empty")
  - /tasks/update – actualiza usando campo `id` desde Cloud Run
  - /tasks/list – devuelve últimas 20 tareas ordenadas por created_at
- Actions OpenAPI:
  - Endpoint: /actions/openapi.json
  - Incluye:
    - /health
    - /meta
    - /natacha/respond
    - /memory/engine/* (core)
    - /tasks/add, /tasks/list, /tasks/update
    - /ops/debug_source, /ops/insights, /ops/snapshot, /ops/snapshots, /ops/summary
- Sanity scripts:
  - scripts/tasks_sanity.sh → OK contra Cloud Run para user_id=sebastian

## RUNTIME & MEMORY – v19.x

- Runtime oficial (local y Cloud Run)
  - EntryPoint: `service_main:app`
  - Docker CMD: `uvicorn service_main:app --host 0.0.0.0 --port 8080`

- Memoria larga (oficial)
  - Engine: `routes/memory_v2.py`
  - Router: `/memory/v2/...`
  - STORAGE (prod): `MEMORY_FILE=gs://natacha-memory-store/memory_store.jsonl`
  - STORAGE (local): `memory_store.jsonl` en el root del proyecto

- Runtimes legacy / auxiliares
  - `natacha_app:app` → runtime legado, solo para debug puntual. No se usa en Cloud Run.
  - `app/app.py` (`app:app`) → app auxiliar de core bridge. No es el runtime principal.

## RUNTIMES HTTP – Natacha API y servicios relacionados

### 1) Natacha API principal (servicio `natacha-api` en Cloud Run)

- Runtime oficial (único entrypoint)
  - Módulo: `service_main.py`
  - App: `service_main:app`
  - Docker CMD (prod): `sh -c "uvicorn service_main:app --host 0.0.0.0 --port \${PORT:-8080}"`
  - Cloud Run:
    - Service: `natacha-api`
    - Env principal:
      - `MEMORY_FILE=gs://natacha-memory-store/memory_store.jsonl`

- Memoria larga (oficial)
  - Engine: `routes/memory_v2.py`
  - Router raíz: `/memory/v2/...`
  - STORAGE (prod): `gs://natacha-memory-store/memory_store.jsonl`
  - STORAGE (local): `memory_store.jsonl` en el root del proyecto

### 2) Runtimes legacy / históricos (NO usar como entrypoint en prod)

Estos módulos existen en el repo pero **no** se usan como entrypoint de Cloud Run:

- `natacha_app.py:app`
  - API legado, hoy solo válido para debug puntual/local.
- `app.py:app`
  - Versión anterior del API monolítico.
- `app/app.py:app`
  - App auxiliar / experimento previo de API.

Regla: cualquier despliegue de `natacha-api` en Cloud Run debe apuntar **siempre** a `service_main:app`.

### 3) Otros servicios FastAPI (infra separada, no `natacha-api`)

Estos runtimes viven en el mismo repo pero representan **otros servicios**:

- `core/app.py:app`
  - Servicio "core".
  - Dockerfile propio: `core/Dockerfile` → `uvicorn natacha_app:app ...`
- `health_monitor/app.py:app`
  - Servicio de health monitor.
  - Usa `Procfile` / Dockerfile propios.
- `memory_console/main.py:app`
  - Consola de memoria (UI).
  - Dockerfile propio: `memory_console/Dockerfile`.
- `memory_console/app.py:app`
  - Variante interna de la consola.
- `natacha_core/app.py:app`
  - Motor Natacha Core (servicio aparte).
- `lab/service_actions.py:app`
  - Servicio de laboratorio / pruebas internas.
- `health_monitor/proxy_cloud_compat.py:app`
  - App pequeña de compatibilidad (proxy del health monitor).

### 4) Entorno de desarrollo (local / Docker dev)

- `Dockerfile.dev`
  - Hoy: `uvicorn natacha_app:app ...` (usa runtime legado solo para dev).
  - Plan futuro (cuando estemos cómodos):
    - Cambiar a: `uvicorn service_main:app --host 0.0.0.0 --port 8080 --reload`
    - Objetivo: que dev y prod apunten al mismo runtime oficial.

