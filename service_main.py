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
        print(f"[MEMORY] Memory index reset {reason}")
    except Exception as e:
        print(f"[MEMORY][WARN] reset skipped: {e}")

# ================================================================
# MEMORY SYNC (Cloud Run safe)
# ================================================================
def load_memory_from_gcs():
    try:
        if os.getenv("K_SERVICE") is None:
            return

        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        p = Path(local_path)

        if p.exists():
            _safe_reset_memory_index("already present")
            return

        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")
        blob.download_to_filename(local_path)

        print("[MEMORY] Synced from GCS")
        _safe_reset_memory_index("after sync")

    except Exception as e:
        print(f"[MEMORY][WARN] sync skipped: {e}")

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

from ops.timeline.router import router as timeline_router
from ops.symbolic.router import router as symbolic_router
from ops.semantic.routes import router as semantic_router
from routes.natacha_routes import router as natacha_router

app.include_router(system_daily_snapshot_router)
app.include_router(system_force_checkpoint_router)
app.include_router(system_diagnose_router)
app.include_router(system_narrative_router)
app.include_router(timeline_router)
app.include_router(symbolic_router)
app.include_router(semantic_router)
app.include_router(natacha_router)
app.include_router(health_router)
app.include_router(get_system_state_router)

print("[OK] routers loaded")

from routes.system_memory_diagnostic_v2 import router as memory_diag_router
app.include_router(memory_diag_router)
print("[OK] memory_diagnostic v2 enabled")

# ================================================================
# STARTUP (FROZEN)
# ================================================================
@app.on_event("startup")
def on_startup():
    start_background(load_memory_from_gcs)

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
