from pymongo import ASCENDING, errors

def ensure_task_indexes(tasks_col):
    """Crea el índice único para evitar tareas duplicadas (pending/vigente)."""
    try:
        tasks_col.create_index(
            [("key", ASCENDING), ("state", ASCENDING)],
            unique=True,
            partialFilterExpression={"state": {"$in": ["pending", "vigente"]}},
            name="uniq_key_state_open"
        )
        print("✅ Índice 'uniq_key_state_open' verificado o creado.")
    except errors.PyMongoError as e:
        print(f"[WARN] No se pudo crear el índice: {e}")
