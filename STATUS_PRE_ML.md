# STATUS_PRE_ML

Fecha: 2025-12-29
Tag: stable-pre-ml
Engine: v17 (shadow)

## Estado general
- Infraestructura: estable (Cloud Run + Firestore)
- Cron snapshot diario: habilitado
- Snapshot engine: operativo
- Checkpoints cognitivos: operativos
- Shadow ML collection: activa
- Training ML: deshabilitado (intencional)

## Decisiones clave
- NO iniciar semantic engine ni embeddings todavía
- NO entrenar modelos antes de cerrar arquitectura
- Guardar datos ML solo en modo shadow
- Avanzar a ML solo desde este tag

## Próximo paso autorizado
→ Diseño de semantic engine + vector memory
→ Sin ejecución hasta validación conceptual

## Semantic Engine
- Initialized: YES
- Mode: heuristic_only
- Vectorization: disabled
- ML training: disabled
- Bootstrap event: semantic_state
