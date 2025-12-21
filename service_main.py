import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

print("[BOOT] service_main import")

# ======================================================
# FASTAPI APP (LIGHTWEIGHT IMPORT)
# ======================================================
app = FastAPI(
    title="Natacha API",
    version="CEREBRO-STABLE",
)

from routes.system_health import router as system_health_router
app.include_router(system_health_router)
print("[OK] system health router enabled")

@app.get("/")
def root():
    return {"status": "ok", "engine": "natacha"}

# ======================================================
# ROUTERS (SAFE IMPORTS ONLY)
# ======================================================
from routes.system_state import router as system_state_router
from routes.system_full_status import router as system_full_status_router
from routes.system_last_checkpoint import router as system_last_checkpoint_router
from routes.system_daily_snapshot import router as system_daily_snapshot_router
from routes.system_force_checkpoint import router as system_force_checkpoint_router
from routes.system_diagnose import router as system_diagnose_router
from routes.system_narrative import router as system_narrative_router
from routes.natacha_routes import router as natacha_router

from ops.timeline.router import router as timeline_router
from ops.symbolic.router import router as symbolic_router
from ops.semantic.routes import router as semantic_router
from ops.semantic.register_state import router as semantic_register_router

app.include_router(system_state_router)
app.include_router(system_full_status_router)
app.include_router(system_last_checkpoint_router)
app.include_router(system_daily_snapshot_router)
app.include_router(system_force_checkpoint_router)
app.include_router(system_diagnose_router)
app.include_router(system_narrative_router)

app.include_router(timeline_router)
app.include_router(symbolic_router)
app.include_router(semantic_router)
app.include_router(semantic_register_router)
app.include_router(natacha_router)

print("[BOOT] routers loaded")

# ======================================================
# STARTUP (ALL HEAVY LOGIC HERE)
# ======================================================
@app.on_event("startup")
def on_startup():
    print("[STARTUP] begin")

    # Memory sync
    try:
        from ops.startup.memory_sync import load_memory_from_gcs
        load_memory_from_gcs()
    except Exception as e:
        print(f"[STARTUP][MEMORY][WARN] {e}")

    # Post-startup worker
    try:
        from ops.startup.post_startup import launch_post_startup
        launch_post_startup()
    except Exception as e:
        print(f"[STARTUP][POST][WARN] {e}")

    # Semantic warmup (non-blocking)
    try:
        from ops.cognitive.semantic_warmup import warmup_semantic_core
        warmup_semantic_core()
    except Exception as e:
        print(f"[STARTUP][SEMANTIC][WARN] {e}")

    # Revision checkpoint
    try:
        from ops.cognitive.auto_checkpoint import write_revision_checkpoint
        write_revision_checkpoint()
    except Exception as e:
        print(f"[STARTUP][CHECKPOINT][WARN] {e}")

    print("[STARTUP] completed")

# ======================================================
# OPENAPI
# ======================================================
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
