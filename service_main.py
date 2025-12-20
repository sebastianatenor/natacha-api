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
from routes.system_daily_snapshot import router as system_daily_snapshot_router
app.include_router(system_daily_snapshot_router)
print("[OK] system_daily_snapshot router enabled")
from routes.system_force_checkpoint import router as system_force_checkpoint_router
app.include_router(system_force_checkpoint_router)
print("[OK] system_force_checkpoint router enabled")

app.include_router(system_state_router)
app.include_router(system_full_status_router)
app.include_router(system_last_checkpoint_router)
from routes.system_daily_snapshot import router as system_daily_snapshot_router
app.include_router(system_daily_snapshot_router)
print("[OK] system_daily_snapshot router enabled")
from routes.system_force_checkpoint import router as system_force_checkpoint_router
app.include_router(system_force_checkpoint_router)
print("[OK] system_force_checkpoint router enabled")

# --- Timeline cognitivo
from ops.timeline.router import router as timeline_router
app.include_router(timeline_router)
print("[OK] timeline router enabled")

# --- Razonamiento simbólico
from ops.symbolic.router import router as symbolic_router
app.include_router(symbolic_router)
print("[OK] symbolic router enabled")

# ================================================================
# Startup
# ================================================================
@app.on_event("startup")
def on_startup():
    start_background(load_memory_from_gcs)
    start_background(run_daily_snapshot)
    start_background(load_vector_index_background)

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

# --- Semantic (lazy, canonical)
try:
    from ops.semantic.routes import router as semantic_router
    app.include_router(semantic_router)
    print("[OK] semantic router enabled")
except Exception as e:
    print(f"[SKIP] semantic router: {e}")


# --- Natacha chat
try:
    from routes.natacha_routes import router as natacha_router
    app.include_router(natacha_router)
    print("[OK] natacha chat router enabled")
except Exception as e:
    print(f"[SKIP] natacha router: {e}")


# =====================================================
# VECTOR INDEX LOAD (NON-BLOCKING)
# =====================================================
def load_vector_index_background():
    try:
        from ops.vector.load_vector_index import load_vector_index_if_exists
        idx = load_vector_index_if_exists()
        if idx:
            print("[STARTUP] Vector index ready")
    except Exception as e:
        print(f"[STARTUP][VECTOR][WARN] {e}")

# =====================================================
# DAILY SNAPSHOT (NON-BLOCKING)
# =====================================================
def run_daily_snapshot():
    try:
        from ops.snapshots.daily_snapshot import write_daily_snapshot
        write_daily_snapshot()
    except Exception as e:
        print(f"[STARTUP][SNAPSHOT][WARN] {e}")
