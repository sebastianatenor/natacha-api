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
