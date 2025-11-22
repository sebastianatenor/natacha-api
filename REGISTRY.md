### semantic_memory_v2 (MEMORIA SEMÁNTICA)

- Rol: memoria de largo plazo basada en Firestore.
- Guarda: texto, tags, personas, timestamp, embedding.
- Endpoints:
    POST /memory/v2/semantic/add
    GET  /memory/v2/semantic/search
    GET  /memory/v2/semantic/summary
- Garantías:
    - Nunca rompe por fallos de OpenAI.
    - Siempre devuelve resultados.
    - summarize() nunca levanta excepción (devuelve fallback).
- Índice Firestore requerido:
    user_id ASC, project ASC, ts DESC.

#### Integración: semantic_memory_v2 ↔ motor de contexto (context_bundle)

Rol de la integración:
- Cuando Natacha necesita “entender en qué anda Sebastián”, el motor de contexto (context_bundle)
  consulta a `semantic_memory_v2` para traer recuerdos relevantes y los mezcla con:
  - memoria reciente / conversación actual
  - tareas abiertas y estado de proyectos (LLVC, etc.)
  - eventos de calendario / signals externos (cuando estén integrados)

Contrato mínimo de uso (desde el engine):
- Siempre llamar a `semantic_memory_v2.summarize(...)` con:
  - `user_id` obligatorio (ej: "sebastian").
  - `project` opcional pero recomendado (ej: "LLVC").
  - `q` la intención actual o tema (ej: "proformas", "estado grúas SQZ400").
  - `limit` entre 3 y 20 según el caso (por defecto usamos 5–10).
- El engine NUNCA debe asumir que:
  - habrá siempre items,
  - habrá siempre embeddings,
  - OpenAI respondió bien.
  En su lugar, debe usar SIEMPRE los campos del dict que devuelve `summarize()`:

Salida garantizada de `semantic_memory_v2.summarize()`:
- `query`: la query original que se usó.
- `user_id`, `project`: eco de los parámetros.
- `limit`: cuántos recuerdos se consideraron.
- `context_preview`: texto compacto con los recuerdos relevantes (`[#1] ...`).
- `summary`: resumen en lenguaje natural (o fallback sin modelo si falló algo).
- `model`: modelo usado (ej: "gpt-4o-mini").
- `error`: `null` si todo ok, o string con el mensaje de error si el modelo falló.
- `items`: lista de recuerdos con sus campos:
  - `text`, `tags`, `people`, `ts`, `project`, `user_id`
  - `score` (similitud coseno básica)
  - `sim` (similitud normalizada interna)
  - `fresh` (factor de frescura / recencia)
  - `tag_bonus` (bonus por match de tags)

Responsabilidad del engine (context_bundle):
- Usar `summary` y/o `context_preview` como “memoria larga” para construir el prompt de Natacha.
- Puede usar `items` para:
  - destacar qué es lo más importante,
  - decidir próximos pasos (ej: “hablar con Sophie por proformas”),
  - alimentar otros módulos (planner, gestor de tareas, etc.).
- No debe escribir directamente en Firestore para memoria semántica:
  SIEMPRE debe delegar las escrituras a `semantic_memory_v2.save_event(...)`
  o a los endpoints `/memory/v2/semantic/add`.

Ejemplo mental de flujo:
1. Usuario habla de “proformas de XCMG para Metalcon”.
2. Engine llama a:
   - `summ = semantic_memory_v2.summarize(user_id="sebastian", project="LLVC", q="proformas", limit=5)`
3. Engine arma el contexto de Natacha con:
   - conversación reciente,
   - `summ["summary"]`,
   - opcionalmente algunos `summ["items"]` crudos.
4. Natacha responde sabiendo:
   - que Sophie está demorada,
   - que hay preocupación por Metalcon y los clientes,
   - que quizá haya que escribir o hacer follow-up.

# Natacha API - Registry
- URL: https://natacha-api-422255208682.us-central1.run.app
- Revisión: natacha-api-00605-9x5
- Service Account: natacha-runtime@asistente-sebastian.iam.gserviceaccount.com
- Secret montado: NATACHA_API_KEY
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


### Módulos legacy adicionales

- `routes/register_core_bridge.py`
  - Tenía un patrón viejo de `app.include_router(...)` acoplado a un runtime global.
  - Hoy NO se importa desde `service_main:app`.
  - Se conserva solo como referencia histórica.
