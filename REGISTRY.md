## Estado actual (2025-10-31 - post deploy 00027-lkf)
- URL pública preferida: https://natacha-api-422255208682.us-central1.run.app
- URL pública secundaria (status Cloud Run): https://natacha-api-mkwskljrhq-uc.a.run.app
- Revisión activa: natacha-api-00027-lkf
- Service Account (runtime): natacha-firestore-access@asistente-sebastian.iam.gserviceaccount.com
- Secret montado: /etc/secrets/firestore-key.json → natacha-firestore-key:latest

## Historial de cambios

### 2025-10-31 – `/memory/search` con `query` opcional
- Cambio: `/memory/search` pasa a aceptar `query` **opcional** y permite listar las últimas memorias.
- Motivo: alinear la API con el comportamiento del Agente Natacha (pedidos sin texto) y preparar integración futura con resúmenes automáticos y búsqueda semántica.
- Impacto: integraciones (ChatGPT / Actions / consola interna) ya pueden hacer `.../memory/search?limit=5` sin error 422.
- Código modificado: `routes/memory_routes.py`
- Desplegado en: `natacha-api-00026-fdx` → **reafirmado en** `natacha-api-00027-lkf`
- Verificado en:
  - `curl -s "http://127.0.0.1:8000/memory/search?limit=5"`
  - `curl -s "https://natacha-api-422255208682.us-central1.run.app/memory/search?limit=5"`

### 2025-10-31 – `/ops/summary` publicado
- Cambio: se publica `/ops/summary` para que el agente pueda leer **memorias + tareas + agrupadas por proyecto** en una sola llamada.
- Motivo: facilitar resúmenes operativos y permitir que el GPT recupere contexto sin tener que hacer 3 requests.
- Código modificado: `routes/ops.py`
- Desplegado en: `natacha-api-00027-lkf`
- Verificado en:
  - `curl -s "http://127.0.0.1:8001/ops/summary?limit=5"`
  - `curl -s "https://natacha-api-422255208682.us-central1.run.app/ops/summary?limit=5"`
  - `curl -s "https://natacha-api-mkwskljrhq-uc.a.run.app/ops/summary?limit=5"`

---

✅ **Validación técnica final – 2025-10-31**
- Estado: **Estable y operativo**
- Revisión validada: `natacha-api-00027-lkf`
- Infraestructura: Cloud Run + Firestore (us-central1)
- Endpoints críticos: `/health`, `/memory/add`, `/memory/search`, `/ops/snapshot`, `/ops/snapshots`, `/ops/summary`
- Resultado final: 🟢 **Infraestructura validada y lista para expansión del agente Natacha.**

### 2025-10-31 – Unificación de OPS (fase 1)
- Cambio: se movió `/ops/summary` al router **oficial** (`routes/ops_routes.py`) porque es el que carga la app de producción (`natacha_app.py`).
- Motivo: evitar duplicaciones entre `routes/ops.py` (histórico) y `routes/ops_routes.py` (oficial) y que las integraciones (ChatGPT / consola / Actions) siempre vean el mismo endpoint.
- Archivos tocados: `routes/ops_routes.py`, `app.py`
- No se eliminó: `routes/ops.py` → queda en modo **compatibilidad** hasta revisar quién más lo usa.
- Verificado en:
  - `http://127.0.0.1:8001/ops/summary?limit=5`
  - `https://natacha-api-422255208682.us-central1.run.app/ops/summary?limit=5`
  - `https://natacha-api-mkwskljrhq-uc.a.run.app/ops/summary?limit=5`

### 2025-10-31 – Unificación parcial de OPS
- Cambio: se replica `/ops/summary` en `routes/ops_routes.py` (el que usa `natacha_app.py`).
- Motivo: evitar que una futura limpieza de `routes/ops.py` deje al agente sin resumen operativo.
- Código modificado: `routes/ops_routes.py`
- Estado: `routes/ops.py` se mantiene **por compatibilidad** (no borrar todavía).
- Verificado en local: `curl -s "http://127.0.0.1:8001/ops/summary?limit=5"`

### 2025-10-31 – Conflicto de nombres `app` resuelto (local)
- Problema: `uvicorn app:app` importaba el paquete `app/` en lugar del módulo `app.py`, ya que existía un `app/__init__.py`.
- Cambio: se renombró `app/` a `app_support_$(date +%Y%m%d%H%M)` para que `app.py` quede como módulo principal y se cargue correctamente.
- Motivo: evitar conflictos entre el paquete `app/` y el archivo principal `app.py` que usa FastAPI.
- Alcance: **solo entorno local** (en Cloud Run ya se usa `natacha_app:app`).
- Verificado con:
  - `python3 - << 'PYCODE' ... import app ...`
  - `uvicorn app:app --reload --port 8002`
- Estado: ✅ corregido y estable

### 2025-11-01 – Limpieza de ops_routes y agregado de /ops/insights
- Cambio: se unificó `/ops/summary` en un solo handler dentro de `routes/ops_routes.py` (había dos).
- Cambio: se agregó `/ops/insights` para entregar memorias + tareas + alertas + duplicados.
- Motivo: evitar conflictos de rutas y darle al agente una vista más inteligente sin tocar endpoints ya usados por integraciones.
- Código modificado: `routes/ops_routes.py`
- Verificado en local:
  - `curl -s "http://127.0.0.1:8002/ops/summary?limit=5"`
  - `curl -s "http://127.0.0.1:8002/ops/insights?limit=20"`

### 2025-11-01 – Arranque con contexto operativo
- Cambio: se creó `intelligence/startup.py` para leer `/ops/insights` y guardar `last_context.json`.
- Cambio: se enganchó el startup en `natacha_app.py` (bloque try/except, no rompe si falla).
- Motivo: que el agente tenga a mano memorias, tareas y proyectos sin hacer 3 requests.
- Verificado en local:
  - `python3 - << 'PYCODE' ... load_operational_context(...) ...`
  - `curl -s "http://127.0.0.1:8002/ops/insights?limit=20"`

### 2025-11-01 – Deploy Cloud Run con contexto remoto
- Servicio: natacha-api
- Revisión: natacha-api-00030-7r4
- Cambio: se agregó env `NATACHA_CONTEXT_API=https://natacha-api-422255208682.us-central1.run.app`
- Motivo: que el startup (`intelligence/startup.py`) use directamente la URL pública en producción.
- Verificado:
  - `curl -s "https://natacha-api-422255208682.us-central1.run.app/ops/insights?limit=20"`
  - `gcloud run services describe natacha-api --region=us-central1 --project=asistente-sebastian --format="value(spec.template.spec.containers[0].env)"`
