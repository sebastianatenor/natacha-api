# REGISTRY — Infra Natacha

## 1. Reglas de trabajo (OBLIGATORIAS)
- Siempre: **cat → nano → docker compose up -d --build <servicio>**
- No duplicar servicios si ya existe uno similar.
- Documentar acá toda cuenta de servicio nueva, colección nueva o endpoint nuevo.
- Proyecto de DATOS: **asistente-sebastian**
- Proyecto de API / runtime: **gen-lang-client-0363543020**

## 2. Docker local (Mac)
- natacha-api → http://localhost:8080
- natacha-core → http://localhost:8081
- natacha-memory-console → http://localhost:8082
- natacha-health-monitor → interno
- natacha-service-checker → interno, escribe en Firestore → **collection:** `system_health`
- keen_heyrovsky → pruebas de health (puerto 8085, hoy UNHEALTHY)

## 3. GCP
### 3.1 Proyecto: asistente-sebastian
- Firestore:
  - `system_health` → estado de servicios (se escribe cada 60s desde el contenedor `natacha-service-checker`)
  - `assistant_memory` → (planificado) memoria de conversaciones / acciones
- Service Accounts:
  - `natacha-checker@asistente-sebastian.iam.gserviceaccount.com`
    - roles: `roles/datastore.user`, `roles/logging.logWriter`
    - key montada en Docker: `/gcloud/natacha-checker.json`
- Montaje en Docker:
  - volume: `${HOME}/.config/gcloud:/gcloud:ro`
  - env: `GOOGLE_APPLICATION_CREDENTIALS=/gcloud/natacha-checker.json`

### 3.2 Proyecto: gen-lang-client-0363543020
- Cloud Run:
  - `https://natacha-api-505068916737.us-central1.run.app`
  - endpoints conocidos: `/` (status), `/tts`
  - pendiente: agregar `/memory/add` y `/memory/search`

## 4. Endpoints previstos para MEMORIA (pendiente de montar en FastAPI)
- POST `/memory/add`
  - body: { "summary": "...", "detail": "...", "channel": "whatsapp|chatgpt|manual", "project": "LLVC" }
  - guarda en Firestore: colección `assistant_memory`
- GET `/memory/search?q=...`
  - trae últimas 20 entradas que contengan el texto

## 5. Pendientes
- [ ] Montar router de memoria en la API local (app main)
- [ ] Replicar en Cloud Run
- [ ] Exponerlo en el GPT “Natacha” (Actions)
- [ ] Agregar entrada de “health” en Notion / Drive (opcional)

## 2025-10-31 — Actualización Cloud Run (Firestore + memoria OK)

- **Servicio:** `natacha-api`
  - **Proyecto:** `asistente-sebastian`
  - **Región:** `us-central1`
  - **URL pública principal:** https://natacha-api-422255208682.us-central1.run.app
  - **Revisión activa:** `natacha-api-00025-5nd`
  - **Imagen:** auto-build desde Dockerfile (python:3.13-slim + FastAPI)
  - **Service Account (runtime):** `natacha-firestore-access@asistente-sebastian.iam.gserviceaccount.com`
  - **Ingress:** all (público)
  - **Secret montado:** `/etc/secrets/firestore-key.json → natacha-firestore-key:latest`
  - **Firestore DB:** (default) — `us-central1`
    - Colecciones: `assistant_memory`, `assistant_tasks`
  - **Endpoints activos:**
    - GET `/health`
    - POST `/memory/add`
    - GET `/memory/search`
    - POST `/tasks/add`
    - GET `/tasks/search`
    - POST `/ops/snapshot`
    - GET `/ops/snapshots`
  - **Notas:**
    - Firestore operativo ✅ (verificado con POST /memory/add)
    - Anteriormente devolvía `403 Missing or insufficient permissions.`
    - Solucionado montando secret con key de `natacha-github@...`
