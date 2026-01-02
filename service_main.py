# service_main.py
import os
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

print("[BOOT] service_main starting")

# ================================================================
# ENV / CONSTANTS
# ================================================================
os.environ.setdefault("PORT", "8080")

IS_CLOUD_RUN = bool(os.getenv("K_SERVICE"))
CANONICAL_MEMORY_PATH = (
    Path("/tmp/memory_store.jsonl")
    if IS_CLOUD_RUN
    else Path("memory_store.jsonl")
)

# ================================================================
# GLOBAL STATE (READ-ONLY)
# ================================================================
COGNITIVE_RESTORE = {
    "restored": False,
    "reason": "not_initialized",
}

# ================================================================
# HELPERS
# ================================================================
def start_background(fn):
    t = threading.Thread(target=fn, daemon=True)
    t.start()


def safe_include(app, import_fn, name: str):
    try:
        router = import_fn()
        app.include_router(router)
        print(f"[ROUTER] loaded: {name}")
    except Exception as e:
        print(f"[ROUTER][SKIPPED] {name}: {e}")


# ================================================================
# MEMORY BOOTSTRAP (GCS → LOCAL CANONICAL)
# ================================================================
def bootstrap_memory():
    print("[MEMORY] bootstrap start")
    print("[MEMORY] canonical path:", CANONICAL_MEMORY_PATH)

    if not IS_CLOUD_RUN:
        CANONICAL_MEMORY_PATH.touch(exist_ok=True)
        print("[MEMORY] local mode → ensured file exists")
        return

    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")

        if blob.exists():
            blob.download_to_filename(CANONICAL_MEMORY_PATH)
            print("[MEMORY] restored from GCS")
        else:
            CANONICAL_MEMORY_PATH.touch(exist_ok=True)
            print("[MEMORY] GCS empty → created new memory file")

    except Exception as e:
        print("[MEMORY][FATAL] bootstrap failed:", e)
        CANONICAL_MEMORY_PATH.touch(exist_ok=True)


# ================================================================
# FASTAPI APP
# ================================================================
app = FastAPI(
    title="Natacha API",
    version="PRE-ML-CANONICAL",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "natacha",
        "mode": "pre-ml",
    }


# ================================================================
# CORE ROUTERS (MÍNIMOS, ESTABLES)
# ================================================================
from routes.health import router as health_router
from routes.get_system_state import router as get_system_state_router
from routes.ops_executive_brief import router as executive_router
from routes.system_restore_status import router as restore_status_router
from routes.memory_recent_canonical import router as memory_recent_router
from routes.system_executive_state import router as executive_state_router
from routes.system_guardrail import router as guardrail_router
from routes.system_state import router as system_state_router
from ops.semantic.startup_guard import semantic_startup_guard
from routes.semantic_status import router as semantic_status_router

app.include_router(health_router)
app.include_router(get_system_state_router)
app.include_router(executive_router)
app.include_router(restore_status_router)
app.include_router(memory_recent_router)
app.include_router(executive_state_router)
app.include_router(guardrail_router)
app.include_router(system_state_router)
app.include_router(semantic_status_router)

print("[ROUTER] core loaded")

# ================================================================
# AGENT INTERACT — COGNITIVE (REAL)
# ================================================================
from ops.agent.interact import router as agent_router
app.include_router(agent_router)
print("[ROUTER] cognitive agent mounted: /agent/interact")

# ================================================================
# AGENT INTERACT — PROXY HACIA NATCHA-OS
# ================================================================
#from fastapi import Request
#import requests
#
#NATACHA_OS_URL = os.getenv(
#    "NATACHA_OS_URL",
#    "https://natacha-os-v7-422255208682.us-central1.run.app"
#)
#
#@app.post("/agent/interact")
#async def agent_interact_proxy(request: Request):
#    payload = await request.json()
#    r = requests.post(
#        f"{NATACHA_OS_URL}/agent/interact",
#        json=payload,
#        timeout=30
#    )
#    return r.json()

# ================================================================
# OPTIONAL ROUTERS (NO BLOQUEAN)
# ================================================================
def load_optional_routers():
    safe_include(app, lambda: __import__("routes.memory_recent", fromlist=["router"]).router, "memory_recent")
    safe_include(app, lambda: __import__("routes.memory_recall", fromlist=["router"]).router, "memory_recall")
    safe_include(app, lambda: __import__("routes.memory_note", fromlist=["router"]).router, "memory_note")

    safe_include(app, lambda: __import__("routes.system_global_status", fromlist=["router"]).router, "system_global_status")
    safe_include(app, lambda: __import__("routes.system_snapshot", fromlist=["router"]).router, "system_snapshot")
    safe_include(app, lambda: __import__("routes.system_checkpoint", fromlist=["router"]).router, "system_checkpoint")
    safe_include(app, lambda: __import__("routes.system_sync", fromlist=["router"]).router, "system_sync")
    safe_include(app, lambda: __import__("routes.system_capabilities", fromlist=["router"]).router, "system_capabilities")

# ================================================================
# STARTUP SEQUENCE (CANÓNICA)
# ================================================================
@app.on_event("startup")
def on_startup():
    global COGNITIVE_RESTORE

    # 0️⃣ Registrar estado semántico REAL (AGENTE_VERAZ)
    semantic_startup_guard()

    # 1️⃣ Bootstrap memory FIRST
    bootstrap_memory()

    # 2️⃣ Load routers
    load_optional_routers()

    # 3️⃣ Restore cognitive state (READ-ONLY)
    try:
        from ops.system.restore_from_memory import restore_cognitive_state

        COGNITIVE_RESTORE = restore_cognitive_state()
        print("[RESTORE] result:", COGNITIVE_RESTORE)

    except Exception as e:
        print("[RESTORE][ERROR]", e)
        COGNITIVE_RESTORE = {
            "restored": False,
            "reason": str(e),
        }

    # 4️⃣ Initialize semantic registry (VERIFIED, unloaded)
    try:
        from ops.cognitive.semantic_registry import register_semantic_event

        register_semantic_event(
            state="unloaded",
            confidence="high",
            source="startup"
        )

        print("[SEMANTIC] registry initialized (unloaded)")

    except Exception as e:
        print("[SEMANTIC][ERROR] registry init failed:", e)


    from ops.cognitive.semantic_registry import register_semantic_event

    register_semantic_event(
        state="unloaded",
        confidence="high",
        source="startup",
    )

    from ops.cognitive.semantic_guard import semantic_startup_guard

    semantic_startup_guard()

    print("[STARTUP] system ready")


# ================================================================
# OPENAPI
# ================================================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="PRE-ML-CANONICAL",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
