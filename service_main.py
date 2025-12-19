import os
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

print("[BOOT] service_main starting")

# ================================================================
# FAST BOOT FLAG
# ================================================================
os.environ.setdefault("NATACHA_FAST_BOOT", "1")

# ================================================================
# Helpers
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
# Memory sync (Cloud Run safe)
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
# FastAPI
# ================================================================
app = FastAPI(
    title="Natacha API",
    version="CEREBRO-STABLE",
)

@app.get("/")
def root():
    return {"status": "ok", "engine": "natacha"}

# ================================================================
# Routers
# ================================================================
from routes.system_state import router as system_state_router
from routes.system_full_status import router as system_full_status_router
from routes.system_last_checkpoint import router as system_last_checkpoint_router
from routes.system_force_checkpoint import router as system_force_checkpoint_router
app.include_router(system_force_checkpoint_router)
print("[OK] system_force_checkpoint router enabled")

app.include_router(system_state_router)
app.include_router(system_full_status_router)
app.include_router(system_last_checkpoint_router)
from routes.system_force_checkpoint import router as system_force_checkpoint_router
app.include_router(system_force_checkpoint_router)
print("[OK] system_force_checkpoint router enabled")

# ================================================================
# Startup
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

    try:
        from ops.cognitive.auto_checkpoint import write_revision_checkpoint
        write_revision_checkpoint()
        print("[STARTUP] Revision checkpoint written")
    except Exception as e:
        print(f"[STARTUP][WARN] checkpoint skipped: {e}")

    print("[STARTUP] completed")

# ================================================================
# OpenAPI
# ================================================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="Natacha Internal API",
        version="CEREBRO-STABLE",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
