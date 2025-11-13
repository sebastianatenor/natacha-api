# MAPA DE ACCIONES – Natacha API

Este documento clasifica las acciones de la API en cuatro grupos:

1. Acciones CORE (las que sí van al OpenAPI público).
2. Acciones útiles pero todavía no prudentes.
3. Acciones internas (no deben exponerse).
4. Acciones viejas / legacy (no se van a usar).

------------------------------------------------------------
1. ACCIONES CORE (VAN AL OPENAPI PÚBLICO)
------------------------------------------------------------

Estas son las que necesita la app / ChatGPT para trabajar con memoria y tareas.

### 1.1 Núcleo de conversación

- **/natacha/respond**
  - Endpoint principal de Natacha.
  - Usa `memory/engine/context_bundle` internamente vía `natacha_brain`.

### 1.2 Motor de memoria oficial (memory_engine)

- **POST /memory/engine/raw**
  - Guarda memorias crudas normalizadas en `memory_raw`.

- **POST /memory/engine/consolidate**
  - Consolida memorias (por `user_id` o global) en `memory_clean`.

- **GET /memory/engine/recent**
  - Devuelve memorias recientes para debug y contexto rápido.

- **GET /memory/engine/context_bundle**
  - Devuelve paquete completo de contexto:
    - `system_rule`
    - `summary`
    - `recent`

### 1.3 Sistema de tareas (tasks)

- **POST /tasks/add**
  - Crea una tarea (title, detail, project, channel, due, state).

- **GET /tasks/list**
  - Lista tareas filtrando por usuario/estado/proyecto.

- **POST /tasks/update**
  - Actualiza estado de una tarea (done, pendiente, etc).

### 1.4 Salud y metadatos

- **GET /health**
  - Healthcheck simple de la API (usado también por `health_memory.sh` y compañía).

- **GET /meta**
  - Metadatos del servicio (nombre, versión, entorno).

👉 **Total CORE actual: 10 acciones.**
Este será el set principal del OpenAPI público para ChatGPT / app.

------------------------------------------------------------
2. ACCIONES ÚTILES PERO TODAVÍA NO PRUDENTES
------------------------------------------------------------

No se exponen todavía porque requieren diseño adicional
(embeddings, vector DB, reglas más maduras, etc).

- **/memory/embed**
- **/memory/search_smart**
- **/memory/search_vector**
- **/memory/v2/store**
- **/memory/v2/search**
- **/memory/v2/compact**
- **/actions/catalog**
- **/ops/summary**

Estas se evaluarán cuando:
- Esté definido el diseño de embeddings,
- Esté madura la estrategia de búsqueda semántica,
- Y Natacha tenga un protocolo de uso más estable.

------------------------------------------------------------
3. ACCIONES INTERNAS (NO EXPONER AL PÚBLICO)
------------------------------------------------------------

Son rutas de operaciones, debugging o CI/CD.
Sirven para observabilidad y mantenimiento, **no para la app**.

Ejemplos:

- **/ops/self_register**
- **/ops/snapshot**
- **/ops/snapshots**
- **/ops/debug_source**
- **/health/debug_source**
- **/health/deps**
- **/dashboard/data**
- **/live**
- **/ready**
- **/openapi.v1.json**
- **/memory/v2/ops/memory-info**

Regla:  
> Estas rutas solo se usan desde scripts internos (health, ops),
> nunca se exportan a ChatGPT ni a integraciones externas.

------------------------------------------------------------
4. ACCIONES VIEJAS / LEGACY / LABORATORIO
------------------------------------------------------------

Rutas que quedaron del inicio del proyecto o de experimentos
y ya no forman parte del diseño actual.

Ejemplos:

- **/auto/list_repo**
- **/auto/plan_refactor**
- **/auto/show_file**
- **/memory/add** (v0)
- **/memory/search** (v0)
- **/v1/memory/add**
- **/v1/memory/search**
- **/v1/tasks/add**
- **/v1/tasks/search**
- **/v1/tasks/update**

Criterio:

- No se documentan en el OpenAPI público.
- No se usan desde nuevas integraciones.
- Si en el futuro se limpian del código, este documento sirve como referencia histórica.

------------------------------------------------------------
5. RESUMEN EJECUTIVO
------------------------------------------------------------

- **CORE (OpenAPI público)**:  
  `/natacha/respond`, `/memory/engine/*`, `/tasks/*`, `/health`, `/meta`.

- **Útiles pero diferidos**:  
  Endpoints de embeddings, memory v2 y herramientas de catálogo/summary.

- **Internas (ops/health/debug)**:  
  Rutas de operación de infraestructura y diagnóstico.

- **Legacy / laboratorio**:  
  Versiones viejas v1/v0 y endpoints de auto-refactor.

Este mapa es la referencia oficial para decidir qué entra
en el OpenAPI público que se va a conectar a ChatGPT, Notion,
Drive, WhatsApp, Meta, Mercado Libre, etc.
