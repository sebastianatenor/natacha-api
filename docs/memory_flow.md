# MEMORY FLOW – Natacha API (Arquitectura y Flujo Completo)
# Documentación interna – LLVC / Natacha

------------------------------------------------------------
1. COMPONENTES DEL SISTEMA DE MEMORIA
------------------------------------------------------------

memory_engine.py
----------------
Motor central del sistema de memoria. Funciones:
- save_raw_memory(): guarda memorias crudas en Firestore (colección memory_raw)
- consolidate_memory(): fusiona memorias crudas en un resumen limpio (memory_clean)
- list_recent_memories(): trae las memorias más recientes
- save_system_rule(): guarda reglas de sistema persistentes
- db = firestore.Client(): cliente Firestore único

Colecciones involucradas:
- memory_raw
- memory_clean
- memory_system


routes/memory_engine_routes.py
------------------------------
API pública del motor de memoria:
- POST /memory/engine/raw
- POST /memory/engine/consolidate
- GET /memory/engine/recent
- POST /memory/engine/system
- GET /memory/engine/context_bundle

Esta API es la interfaz oficial para guardar, leer y consolidar memoria.


natacha_brain.py
----------------
Capa intermedia que procesa la memoria para el modelo:
- fetch_context(): consulta /memory/engine/context_bundle
- build_prompt(): construye el prompt base (reglas + memoria + advertencias)

Esta capa genera el contexto final que Natacha usa para responder.


routes/natacha_routes.py
------------------------
Expone:
POST /natacha/respond

Proceso:
1. Llama a fetch_context()
2. Construye prompt base con build_prompt()
3. Agrega tu mensaje actual
4. Llama al modelo (si hay OPENAI_API_KEY)
5. Devuelve JSON siempre controlado (sin errores 500)

Esta es la ruta que usa ChatGPT Actions y tu integración futura.


------------------------------------------------------------
2. FLUJO DE MEMORIA COMPLETO
------------------------------------------------------------

A) Guardar una memoria cruda
----------------------------
Clientes externos llaman:

POST /memory/engine/raw
→ memory_engine.save_raw_memory()
→ Guarda en Firestore en memory_raw/


B) Consolidación de memoria
---------------------------
POST /memory/engine/consolidate?user_id=sebastian

Genera:
memory_clean/{user_id}
o
memory_clean/global

El resumen final se usa para construir el contexto del modelo.


C) Construcción del contexto para Natacha
------------------------------------------
Cuando enviás:

POST /natacha/respond

El flujo es:

natacha_routes →
    fetch_context() →
        /memory/engine/context_bundle →
            {
              system_rule,
              summary,
              recent
            }
    build_prompt()
    llamada al modelo


------------------------------------------------------------
3. COLECCIONES FIRESTORE UTILIZADAS
------------------------------------------------------------

- memory_raw      (memorias crudas)
- memory_clean    (resúmenes consolidados)
- memory_system   (reglas internas persistentes)


------------------------------------------------------------
4. ESTADO ACTUAL DEL SISTEMA
------------------------------------------------------------

Archivos importantes ya versionados en Git:
- memory_engine.py
- routes/memory_engine_routes.py
- natacha_brain.py
- routes/natacha_routes.py
- docs/agent_rules.md
- seeds/seed_system_rule.json

El directorio lab/ fue eliminado, pero está archivado en Git en la rama:
lab/experimental-memory-actions

El motor oficial es SOLO:
memory_engine.py


------------------------------------------------------------
5. COMPORTAMIENTO ACTUAL
------------------------------------------------------------

- La memoria se guarda correctamente en memory_raw
- La consolidación funciona y genera un resumen limpio
- context_bundle entrega system_rule + summary + recent
- Natacha responde usando ese contexto
- No hay motores viejos interfiriendo
- No hay rutas ocultas
- La arquitectura quedó limpia y unificada


------------------------------------------------------------
6. PRÓXIMOS PASOS RECOMENDADOS
------------------------------------------------------------

1. Agregar consolidación automática programada
2. Agregar embeddings opcionales para búsquedas avanzadas
3. Integrar memoria automática con WhatsApp y Notion
4. Versionar reglas de sistema (core-v2, core-v3…)
5. Usar memory_clean para personalizar prompts de logística y ventas


------------------------------------------------------------
7. RESUMEN FINAL
------------------------------------------------------------

Esta es la arquitectura oficial y estable de memoria:
- memory_engine.py controla todo
- context_bundle entrega el estado completo
- natacha_brain construye el contexto para el modelo
- natacha_routes llama al modelo con ese contexto

El sistema ahora es estable, consistente, mantenible y listo para escalar.

------------------------------------------------------------
8. DIAGRAMA COMPLETO DEL FLUJO DE MEMORIA
------------------------------------------------------------

                +------------------+
                |  Client (You)    |
                |  WhatsApp / CLI  |
                +--------+---------+
                         |
                         | POST /memory/engine/raw
                         v
                +----------------------+
                |  save_raw_memory()   |
                |  Firestore: memory_raw
                +----------------------+
                         |
                         | (manual o cron futuro)
                         v
                +----------------------+
                | consolidate_memory() |
                | Firestore: memory_clean
                +----------------------+
                         |
                         | GET /memory/engine/context_bundle
                         v
                +----------------------+
                |  context_bundle      |
                |  system + summary +  |
                |  recent              |
                +----------------------+
                         |
                         | fetch_context()
                         v
                +----------------------+
                |   build_prompt()     |
                +----------------------+
                         |
                         | POST /natacha/respond
                         v
                +----------------------+
                |      Modelo LLM      |
                +----------------------+
                         |
                         v
                +----------------------+
                |   Respuesta final    |
                +----------------------+

------------------------------------------------------------
9. EJEMPLO COMPLETO END-TO-END
------------------------------------------------------------

# 1) Guardar memoria cruda
POST /memory/engine/raw
{
  "user_id": "sebastian",
  "note": "Recordar empujar proforma con Sophie",
  "kind": "tarea",
  "importance": "alta"
}

# 2) Consolidar
POST /memory/engine/consolidate?user_id=sebastian

# 3) Leer contexto
GET /memory/engine/context_bundle?user_id=sebastian&recent_limit=10

# 4) Preguntar a Natacha
POST /natacha/respond
{
  "user_id": "sebastian",
  "message": "Natacha, ¿qué pendientes tengo?"
}

------------------------------------------------------------
10. DEBUGGING – COMANDOS RÁPIDOS
------------------------------------------------------------

# Quick health
curl -s "$SERVICE_URL/health" | jq

# Ver memorias crudas recientes
curl -s "$SERVICE_URL/memory/engine/recent?user_id=sebastian" | jq

# Ver resumen consolidado
curl -s "$SERVICE_URL/memory/engine/context_bundle?user_id=sebastian" | jq

# Probar flow entero
BASE="$SERVICE_URL" scripts/health_memory.sh

------------------------------------------------------------
11. FALLBACKS Y MECANISMOS DE SEGURIDAD
------------------------------------------------------------

- Si Firestore falla → fetch_context() devuelve error seguro.
- Natacha siempre responde con JSON estructurado, nunca 500.
- build_prompt() incluye "(⚠️ CONTEXT WARNING)" si hay fallos.
- consolidate_memory() ignora errores individuales de documentos.
- Los índices no bloquean: hay fallback a consultas sin filtro.

------------------------------------------------------------
12. EXTENSIÓN A FUTURO (core-v2, core-v3)
------------------------------------------------------------

- Nuevas reglas de sistema versionadas:
  - memory_system/core-v1  (actual)
  - memory_system/core-v2  (próxima)

- Nuevos campos en memoria cruda:
  - tema
  - cliente
  - prioridad extendida
  - timestamp local

- Posible segmentación de memoria:
  - importaciones
  - logística
  - tareas LLVC
  - salud & hábitos (ayuno)
  - e-commerce

------------------------------------------------------------
13. CATEGORÍAS DE MEMORIA RECOMENDADAS
------------------------------------------------------------

Estas son las categorías que Natacha debería aprender a guardar automáticamente:

1. **Tareas y follow-ups**
2. **Relaciones con proveedores**
3. **Reglas del negocio (LLVC)**
4. **Preferencias personales del usuario**
5. **Estados de proyectos LLVC**
6. **Logística internacional y costos**
7. **Pendientes con Sophie, Jamin, Hermes y otros**
8. **Recordatorios diarios**
9. **Ayuno intermitente y hábitos**
10. **Contexto emocional (si aplica en el futuro)**

------------------------------------------------------------
14. ESTADO FINAL DEL DISEÑO
------------------------------------------------------------

El diseño actual es:
- Simple
- Extensible
- Con rutas limpias
- Sin archivos huérfanos
- Con memoria consolidada realmente funcionando
- Listo para embeddings y automatización futura

**Este documento ahora es el blueprint oficial de la memoria de Natacha.**
