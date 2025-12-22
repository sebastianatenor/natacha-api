import os
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from routes.health import router as health_router
from routes.get_system_state import router as get_system_state_router

print("[BOOT] service_main starting")

# ================================================================
# ENV
# ================================================================
os.environ.setdefault("NATACHA_FAST_BOOT", "1")
os.environ.setdefault("PORT", "8080")
os.environ.setdefault("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")

# ================================================================
# HELPERS
# ================================================================
def start_background(fn):
    t = threading.Thread(target=fn, daemon=True)
    t.start()


def _safe_reset_memory_index(reason: str = ""):
    try:
        from unified_core.memory_lazy import reset_memory_index
        reset_memory_index()
        print(f"[MEMORY] Memory index reset ({reason})")
    except Exception as e:
        print(f"[MEMORY][WARN] reset skipped: {e}")

# ================================================================
# CANONICAL MEMORY BOOTSTRAP (GCS → /tmp)
# ================================================================
def bootstrap_memory():
    """
    Canonical memory bootstrap.
    Restores memory_store.jsonl from GCS into /tmp on startup.
    """
    try:
        # Solo en Cloud Run
        if os.getenv("K_SERVICE") is None:
            print("[MEMORY] Local run detected, bootstrap skipped")
            return

        local_path = Path(os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl"))

        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")

        if blob.exists():
            blob.download_to_filename(local_path)
            print("[MEMORY] Canonical memory restored from GCS")
        else:
            local_path.touch(exist_ok=True)
            print("[MEMORY] No remote memory found, initialized empty store")

        _safe_reset_memory_index("after bootstrap")

    except Exception as e:
        print(f"[MEMORY][ERROR] bootstrap failed: {e}")

# ================================================================
# FASTAPI APP
# ================================================================
app = FastAPI(
    title="Natacha API",
    version="BASELINE-v1.0",
)

@app.get("/")
def root():
    return {"status": "ok", "engine": "natacha"}

# ================================================================
# ROUTERS
# ================================================================
from routes.system_daily_snapshot import router as system_daily_snapshot_router
from routes.system_force_checkpoint import router as system_force_checkpoint_router
from routes.system_diagnose import router as system_diagnose_router
from routes.system_narrative import router as system_narrative_router
from routes.system_memory_diagnostic_v2 import router as memory_diag_router
from routes.natacha_routes import router as natacha_router
from routes.memory_recent import router as memory_recent_router
from routes.memory_recall import router as memory_recall_router
from routes.memory_note import router as memory_note_router
from routes.memory_index import router as memory_index_router

from ops.timeline.router import router as timeline_router
from ops.symbolic.router import router as symbolic_router
from ops.semantic.routes import router as semantic_router

app.include_router(system_daily_snapshot_router)
app.include_router(system_force_checkpoint_router)
app.include_router(system_diagnose_router)
app.include_router(system_narrative_router)
app.include_router(memory_diag_router)
app.include_router(memory_recent_router)
app.include_router(memory_index_router)

app.include_router(timeline_router)
app.include_router(symbolic_router)
app.include_router(semantic_router)
app.include_router(natacha_router)
app.include_router(health_router)
app.include_router(get_system_state_router)
app.include_router(memory_recall_router)
app.include_router(memory_note_router)

print("[OK] routers loaded")


@app.get("/__debug/memory_recent")
def debug_memory_recent(limit: int = 20):
    from ops.timeline.reader import read_events
    events = read_events()
    return {
        "status": "ok",
        "count": min(len(events), limit),
        "events": events[-limit:]
    }

# ================================================================
# STARTUP
# ================================================================
@app.on_event("startup")
def on_startup():
    # 1️⃣ Bootstrap memoria canónica (GCS → /tmp)
    bootstrap_memory()

    # 2️⃣ Post-startup async (si existe)
    try:
        from ops.startup.post_startup import launch_post_startup
        start_background(launch_post_startup)
        print("[STARTUP] post_startup launched")
    except Exception as e:
        print(f"[STARTUP][WARN] post_startup skipped: {e}")

    print("[STARTUP] baseline v1.0 ready")

# ================================================================
# OPENAPI
# ================================================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="BASELINE-v1.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
