### semantic_memory_v2 (MEMORIA SEMÁNTICA)

- Rol: memoria de largo plazo basada en Firestore (eventos semánticos por usuario/proyecto).
- Guarda: `text`, `tags`, `people`, `timestamp (ts)`, `project`, `user_id`, `embedding`, scores internos.
- Endpoints:
    POST /memory/v2/semantic/add
    GET  /memory/v2/semantic/search
    GET  /memory/v2/semantic/summary
- Garantías:
    - No rompe por fallos de OpenAI: ante error devuelve fallback (`error != null`, `summary` genérico).
    - Siempre devuelve resultados (aunque sea un resumen vacío/fallback).
    - `summarize()` nunca levanta excepción hacia arriba.
- Índice Firestore requerido:
    - `user_id ASC, project ASC, ts DESC`.

#### semantic_memory_v2 – Dedupe & compaction v1

**Objetivo:**  
Reducir ruido en la memoria semántica consolidando recuerdos muy parecidos en un único recuerdo canónico por “tema”.

**Scope:**  
Eventos de `semantic_memory_v2` para un mismo `user_id` y `project`.

**Detección de candidatos a dedupe (cluster):**
- Mismo `user_id` y `project`.
- Tags solapados fuertemente (ej.: `["xcmg","sophie","gruas","proformas","llvc"]` y variantes con `metalcon`, `sqz400`, `clientes`).
- Alta similitud semántica entre los textos (`text`) según embedding.
- Timestamps cercanos (p. ej. dentro de una ventana de ~7 días) o duplicados exactos.

**Regla de compactación:**
1. Agrupar todos los recuerdos similares en un “cluster de tema” (ej.: `LLVC / Metalcon / grúas SQZ400.4 / Sophie / Jamin`).
2. Definir un **recordatorio maestro** (canónico) que:
   - Condense la información clave de todos los recuerdos del cluster.
   - Use un texto claro, ejecutivo y completo.
   - Use `tags` = unión de todos los tags relevantes del cluster  
     (ej.: `["llvc","metalcon","gruas","sqz400","xcmg","sophie","jamin","proformas","produccion","clientes"]`).
   - Tome `importance` = la máxima importancia del cluster (`high`/`alta`).
3. Conservar solo el recuerdo canónico (nuevo o uno existente actualizado).
4. El resto de recuerdos del cluster:
   - Quedan marcados como `archivados`/`compactados` o se excluyen de búsquedas activas (según imple).

**Regla general:**
- Por cada “tema caliente” debe existir **máximo 1–2 recuerdos activos** en `semantic_memory_v2`.
- El resto de variaciones se compactan o se ignoran por defecto.

**Ejemplo concreto (Sophie & Jamin / Metalcon / SQZ400.4):**
- Cluster original:
  - "Sophie de XCMG está demorada con las proformas de las grúas y necesito mantener la tranquilidad de mis clientes."
  - "Con Sophie de XCMG estamos demorados con las proformas de las grúas para Metalcon."
  - "Con Jamin estamos esperando el VIN y el estado de producción de las dos grúas SQZ400.4 para Metalcon."
  - "Estoy preocupado por el estado de producción de las grúas y las proformas para que Metalcon y mis clientes estén tranquilos."
- Se compacta en un único recuerdo canónico, que menciona:
  - Demoras de proformas con Sophie (XCMG).
  - VIN + estado de producción de las SQZ400.4 con Jamin.
  - Tranquilidad de Metalcon y clientes de LLVC como motivador principal.

---

### Context Engine / `context_bundle` – Contrato funcional v2

**Nombre lógico:** `context_bundle`  
**Responsabilidad:** Construir un “paquete de contexto ejecutivo” para Natacha a partir de distintas memorias y fuentes de datos, listo para prompts de sistema / razonamiento.

---

#### 1. Endpoint y firma

- **HTTP:** `GET /memory/engine/context_bundle`
- **Parámetros (query):**
  - `user_id` (string, requerido) → Identifica al humano (ej.: `"sebastian"`).
  - `project` (string, opcional) → Foco actual (ej.: `"LLVC"`).
    - Si viene, se privilegia contexto de ese proyecto.
    - Si no viene, se usa contexto global del usuario.
  - `limit` (int, opcional, default 20) → Cantidad máxima de ítems por fuente (cuando aplica).

  - **Parámetros semánticos opcionales (semantic_memory_v2):**
    - `semantic_project` (string, opcional) → Proyecto lógico de semantic_v2.  
      - Si no viene y `project` está presente, el engine puede usar `semantic_project = project` como default.
    - `semantic_q` (string, opcional) → Query semántica principal (ej.: `"estado LLVC"`, `"proformas grúas"`).
      - Si no viene, el engine puede usar un default estándar del tipo:  
        `"estado actual y próximos pasos del proyecto"`.
    - `semantic_limit` (int, opcional, default 5) → Límite de recuerdos semánticos.

- **Respuesta (JSON, contrato mínimo):**
  - `summary` (objeto)
    - `summary` (string) → Resumen ejecutivo en español, listo para pegar como contexto.
    - `highlights` (lista de strings) → Bullets con puntos clave.
    - `next_steps` (lista de strings) → Próximos pasos accionables para Natacha / Sebastián.
  - `sources` (objeto) → De dónde salió la info.
    - `semantic` / `semantic_v2` (lista de eventos o resumen semántico).
    - `tasks` (lista de tareas).
    - `recent` / `short_memory` (mensajes recientes).
    - Futuras fuentes (calendar, mail, docs, etc.).
  - `meta` (objeto)
    - `user_id`
    - `project` (si vino)
    - `generated_at` (timestamp)
    - `engine_version` (ej.: `"context_bundle_v2"`)

> Regla: el contrato asegura que siempre exista `summary.summary` (string) aunque alguna fuente falle; en el peor caso será un resumen fallback.

---

#### 2. Fuentes de información que puede consultar

`context_bundle` NO almacena por sí mismo; solo **orquesta**:

1. **Memoria semántica v2** (`semantic_memory_v2`)
   - Vía:
     - `semantic_memory_v2.search(user_id, project?, q?, limit)`
     - `semantic_memory_v2.summarize(user_id, project?, q, limit)`
   - Uso típico:
     - Query genérica del estado actual del proyecto (ej.: `"estado LLVC"`).
     - Queries específicas (ej.: `"proformas grúas"`, `"estado grúas SQZ400"`).
     - Traer eventos relevantes y meterlos al resumen ejecutivo.

2. **Tareas / Task Engine**
   - Tareas abiertas para `user_id` y `project`.
   - Próximos vencimientos relevantes.

3. **Memorias de corto plazo / interacción reciente**
   - Últimos turnos de conversación.

4. **Otras fuentes futuras**
   - Calendario, e-mail, archivos/docs resumidos.

---

#### 3. Reglas de negocio del `context_bundle`

1. **Seguridad ante fallos**
   - Si una fuente falla (Firestore, OpenAI, Notion, etc.):
     - Se captura el error.
     - Se registra en `meta.errors.<fuente>`.
     - El engine **igual devuelve un `summary.summary`** válido (fallback si hace falta).

2. **Priorización de información**
   - Orden de prioridad conceptual:
     1. Estado actual crítico del proyecto (`semantic_memory_v2` → `summarize()`).
     2. Tareas pendientes / próximas acciones (Task engine).
     3. Interacción reciente.
   - El `summary` debe responder a:  
     > “¿En qué estamos con este usuario/proyecto **ahora mismo** y qué deberíamos hacer después?”

3. **Formato del resumen**
   - Siempre en español.
   - Estilo conciso y ejecutivo.
   - Debe incluir:
     1. Resumen breve (2–4 frases).
     2. Puntos clave (bullets).
     3. Próximos pasos sugeridos (bullets).

4. **Uso de `semantic_memory_v2`**
   - El engine respeta el contrato:
     - `query`, `user_id`, `project`, `limit`, `context_preview`, `summary`, `model`, `error`, `items` con `text`, `tags`, `people`, `ts`, `project`, `user_id`, `score`, `sim`, `fresh`, `tag_bonus`.
   - No asume estructura distinta a la documentada.

---

#### 4. Construcción del summary ejecutivo v2
(cómo fusionar macro + semantic_v2 + tareas)

Cuando `context_bundle` arme el objeto `summary`, debe combinar tres capas:

1. **Visión macro / contexto estable**  
   - Fuente: resumen ejecutivo de alto nivel (brief de LLVC + rol de Natacha).
   - Contenido típico:
     - Qué es LLVC / LLVC Global.
     - Rol de Natacha (asistente ejecutiva para importaciones, e-commerce B2B, agentes, etc.).

2. **Estado semántico actual del proyecto**  
   - Fuente: `semantic_memory_v2.summarize(...)` usando:
     - `user_id`
     - `project` o `semantic_project`
     - `semantic_q` (ej.: `"estado LLVC"`, `"proformas grúas"`)
     - `semantic_limit`
   - Contenido típico:
     - Qué está pasando HOY (ej.: VIN SQZ400.4, proformas demoradas, clientes preocupados).
     - Riesgos / temas calientes.

3. **Tareas y próximos pasos operativos**  
   - Fuente: Task engine (`/tasks/list`) + hints de semantic_v2.
   - Contenido típico:
     - Tareas abiertas relevantes.
     - Próximas acciones concretas (contactar, empujar, revisar, informar).

**Regla de ensamblado de `summary.summary`:**

1. Bloque 1 – Visión macro (1–2 frases).
2. Bloque 2 – Estado actual semántico (2–4 frases) usando `semantic_v2.result.summary`.
3. Bloque 3 – Próximos pasos críticos (1–3 frases) combinando:
   - Sugerencias de semantic_v2 (si las hay).
   - Tareas relevantes del Task engine.

**Campos `highlights` y `next_steps`:**

- `highlights`:
  - 3–7 bullets con puntos clave del estado actual.
  - Derivados de `semantic_v2.context_preview` + visión macro.

- `next_steps`:
  - 3–7 bullets con acciones concretas.
  - Derivados de:
    - `semantic_v2.result.summary` (si sugiere acciones).
    - Tareas del Task engine.
    - Reglas de negocio (ej.: avisar a Metalcon cuando haya novedades de VIN/proformas).

**Regla de frescura:**

- Cada llamada a `context_bundle`:
  - Si hay nuevos eventos en semantic_v2 o cambios recientes en tareas:
    - Se regenera el summary para reflejar el estado más reciente.
  - `summary.updated_at` debe reflejar cuándo se generó el summary actual.

---

#### 5. Responsabilidades explícitas

- **Hace:**
  - Agrega contexto disperso en un solo objeto.
  - Traduce memoria + tareas + contexto reciente a un resumen ejecutivo usable.
  - Expone ese contexto como API estable (`/memory/engine/context_bundle`).

- **NO hace:**
  - No define políticas de negocio.
  - No envía mensajes, no crea tareas, no escribe en Firestore.
  - No hace razonamiento de largo plazo; prepara el “paquete de contexto”.

---

#### 6. Versionado y evolución

- `engine_version` en `meta` es obligatorio.
- Este documento define el contrato **v2** del `context_bundle`.
- Cambios breaking → requieren:
  - Bump a `context_bundle_v3`.
  - Actualizar REGISTRY.
  - Ajustar clientes.

---

#### 7. Owner

- **Owner funcional:** Sebastián (producto / estrategia).
- **Owner técnico:** Natacha API (módulo `engine/context_bundle`, integraciones con `semantic_memory_v2`, Task engine y futuras fuentes).

---

## Natacha API - Registry (Cloud Run)

**Estado actual verificado (Cloud Run real, 2025-11-22):**

- URL: `https://natacha-api-422255208682.us-central1.run.app`
- Revisión activa: `natacha-api-00028-w52`
- Service Account actual: `422255208682-compute@developer.gserviceaccount.com`
- Secret montado: `NATACHA_API_KEY`
- Health: `/health` → OK

**Memoria:**
- Engine de contexto:
  - `/memory/engine/recent`
  - `/memory/engine/context_bundle`
  - `system_rule` y `summary` funcionando para `user_id=sebastian`.
- Memoria larga v2 (JSONL):
  - Backend actual: `local`
  - Archivo: `memory_store.jsonl`
  - Ejemplo reciente (`/memory/v2/ops/memory-info`):
    - `count ≈ 4` (estado inicial / baja población).

**Tasks (Task Engine):**
- `/tasks/add` – crea bien tareas (sin error `"values must be non-empty"`).
- `/tasks/update` – actualiza usando campo `id` (Cloud Run).
- `/tasks/list` – devuelve últimas 20 tareas ordenadas por `created_at`.

**Actions OpenAPI:**
- Endpoint: `/actions/openapi.json`
- Incluye:
  - `/health`
  - `/meta`
  - `/natacha/respond`
  - `/memory/engine/*` (core)
  - `/tasks/add`, `/tasks/list`, `/tasks/update`
  - `/ops/debug_source`, `/ops/insights`, `/ops/snapshot`, `/ops/snapshots`, `/ops/summary`

**Sanity scripts:**
- `scripts/tasks_sanity.sh` → OK contra Cloud Run para `user_id=sebastian`.
- `scripts/registry_check.py` → compara REGISTRY vs Cloud Run:
  - Debe ver:
    - URL = `https://natacha-api-422255208682.us-central1.run.app`
    - Revisión = `natacha-api-00028-w52`
    - Service Account = `422255208682-compute@developer.gserviceaccount.com`
    - Secret = `NATACHA_API_KEY`

> Nota: si en el futuro se migra la Service Account a `natacha-runtime@asistente-sebastian.iam.gserviceaccount.com`,  
> primero se cambia en Cloud Run y luego se actualiza este bloque para que `registry_check` vuelva a quedar en verde.

---

## RUNTIME & MEMORY – v19.x

- Runtime oficial (local y Cloud Run)
  - EntryPoint: `service_main:app`
  - Docker CMD: `uvicorn service_main:app --host 0.0.0.0 --port 8080`

- Memoria larga (oficial v2)
  - Engine: `routes/memory_v2.py`
  - Router: `/memory/v2/...`
  - STORAGE (prod): `MEMORY_FILE=gs://natacha-memory-store/memory_store.jsonl`
  - STORAGE (local): `memory_store.jsonl` en el root del proyecto.

- Runtimes legacy / auxiliares
  - `natacha_app:app` → runtime legado, solo para debug puntual (no se usa en Cloud Run).
  - `app/app.py:app` → app auxiliar de core bridge (no es runtime principal).

---

## RUNTIMES HTTP – Natacha API y servicios relacionados

### 1) Natacha API principal (servicio `natacha-api` en Cloud Run)

- Runtime oficial (único entrypoint en prod):
  - Módulo: `service_main.py`
  - App: `service_main:app`
  - Docker CMD (prod):  
    `sh -c "uvicorn service_main:app --host 0.0.0.0 --port ${PORT:-8080}"`

- Env principal:
  - `MEMORY_FILE=gs://natacha-memory-store/memory_store.jsonl`

### 2) Runtimes legacy / históricos (NO usar como entrypoint en prod)

Estos módulos existen en el repo pero **no** se usan como entrypoint de `natacha-api`:

- `natacha_app.py:app`
- `app.py:app`
- `app/app.py:app`

Regla: cualquier despliegue de `natacha-api` en Cloud Run debe apuntar **siempre** a `service_main:app`.

### 3) Otros servicios FastAPI (infra separada, no `natacha-api`)

- `core/app.py:app`
  - Servicio "core".
  - Dockerfile propio: `core/Dockerfile` → `uvicorn natacha_app:app ...`
- `health_monitor/app.py:app`
  - Servicio de health monitor (usa Procfile / Dockerfile propios).
- `memory_console/main.py:app`
  - Consola de memoria (UI) – `memory_console/Dockerfile`.
- `memory_console/app.py:app`
  - Variante interna de la consola.
- `natacha_core/app.py:app`
  - Motor Natacha Core (servicio aparte).
- `lab/service_actions.py:app`
  - Servicio de laboratorio / pruebas internas.
- `health_monitor/proxy_cloud_compat.py:app`
  - Proxy de compatibilidad del health monitor.

### 4) Entorno de desarrollo (local / Docker dev)

- `Dockerfile.dev`
  - Hoy: `uvicorn natacha_app:app ...` (runtime legado solo para dev).
  - Objetivo futuro:
    - Cambiar a:  
      `uvicorn service_main:app --host 0.0.0.0 --port 8080 --reload`
    - Para que dev y prod apunten al mismo runtime oficial.

## Exec Layer – LLVC (Natacha Brain & Tareas)

### Endpoints clave

- `GET /natacha/healthcheck`
  - Descripción: Healthcheck ejecutivo de Natacha para un `user_id` y `project`.
  - Uso: verifica system_rule, summary, memorias recientes, semantic_v2 y conexión al motor de tareas.
  - Estado: 🟢 Estable en producción (Cloud Run).

- `POST /natacha/respond`
  - Descripción: Fachada conversacional de Natacha (usa context_bundle y system_rule core-v1).
  - Uso: interface principal para chat ejecutivo con memoria.

- `GET /tasks/list`
  - Descripción: Lista tareas crudas desde Firestore.
  - Uso recomendado: sin filtros de query; los filtros se aplican del lado del cliente (scripts).
  - Estado: 🟢

- `GET /tasks/list?user_id=...&project=...`
  - Descripción: Versión filtrada por querystring.
  - Estado: 🔴 NO USAR (actualmente devuelve 500). 
  - Workaround: usar `/tasks/list` y filtrar en scripts (ej: `tasks_urgency.py`, `tasks_deepcheck.py`).

### Scripts ejecutivos

- `scripts/tasks_urgency.py`
  - Función: obtiene `/tasks/list`, filtra por `user_id` + `project` y asigna `urgency_score` (ALTA/MEDIA/BAJA).
  - Estado: 🟢 Usar para priorizar tareas LLVC.

- `scripts/exec_status.py`
  - Función: ejecuta health-check integrado de API, Natacha Brain y tareas (con urgencia).
  - Estado: 🟢 Punto de entrada para ver “estado ejecutivo” de LLVC.

- `scripts/tasks_deepcheck.py`
  - Función: diagnóstico profundo de las tareas LLVC (campos faltantes, integridad).
  - Estado: 🟢 Usar antes de hacer limpieza o refactors.

- `scripts/what_now_llvc.py`
  - Función: responde “qué es lo más importante para LLVC ahora mismo” usando urgencias.
  - Estado: 🟢 Herramienta de foco diario para Sebastián.

### Notas

- Este stack forma la **capa ejecutiva** de LLVC dentro de Natacha.
- Siempre que se cambie algo en tareas, memoria o Natacha Brain, correr:
  - `scripts/exec_status.py --user sebastian --project LLVC`
  - `scripts/tasks_deepcheck.py`
