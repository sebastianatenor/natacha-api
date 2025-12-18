import os
import threading
import time
from pathlib import Path

print("[BOOT] service_main loaded — before FastAPI init")

# ================================================================
# FAST BOOT FLAG (CRÍTICO PARA CLOUD RUN)
# ================================================================
os.environ.setdefault(
    "NATACHA_FAST_BOOT",
    os.getenv("NATACHA_FAST_BOOT", "1")
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

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
        print(f"[MEMORY] Memory index reset {f'({reason})' if reason else ''}")
    except Exception as e:
        print(f"[MEMORY][WARN] Could not reset memory index: {e}")

# ================================================================
# 1) BOOT SEQUENCE – Memory Sync (CLOUD RUN SAFE)
# ================================================================

def load_memory_from_gcs():
    try:
        in_cloud_run = os.getenv("K_SERVICE") is not None
        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        p = Path(local_path)

        if not in_cloud_run:
            print("[BOOT] Local environment: skipping memory sync.")
            return

        if p.exists():
            print("[BOOT] Memory already present, skipping GCS sync.")
            _safe_reset_memory_index("memory already present on boot")
            return

        print("[BOOT] Cloud Run detected. Starting async memory sync…")

        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(
            os.getenv("NATACHA_MEMORY_BUCKET", "natacha-memory-store")
        )
        blob = bucket.blob(
            os.getenv("NATACHA_MEMORY_BLOB", "memory_store.jsonl")
        )
        blob.download_to_filename(local_path)

        print("[OK] Memory synced from GCS")
        _safe_reset_memory_index("after GCS sync")

    except Exception as e:
        print(f"[WARN] Memory sync skipped: {e}")

def wait_and_reset_memory_index():
    try:
        if os.getenv("K_SERVICE") is None:
            return

        p = Path(os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl"))
        max_wait = int(os.getenv("NATACHA_MEMORY_WAIT_SECONDS", "30"))
        step = float(os.getenv("NATACHA_MEMORY_WAIT_STEP", "0.5"))

        waited = 0.0
        while waited < max_wait:
            if p.exists() and p.stat().st_size > 0:
                _safe_reset_memory_index("waiter detected memory file ready")
                return
            time.sleep(step)
            waited += step

        print(f"[MEMORY][WARN] memory_store.jsonl not ready after {max_wait}s")
    except Exception as e:
        print(f"[MEMORY][WARN] waiter failed: {e}")

# ================================================================
# 2) FASTAPI INIT
# ================================================================

app = FastAPI(
    title="Natacha API",
    version="CEREBRO-v1-FROZEN",
    description="Natacha – Cloud Run safe fast boot"
)

# ================================================================
# 3) CORE ROUTERS
# ================================================================

# Chat humano (Natacha)
from routes.natacha_routes import router as natacha_router
app.include_router(natacha_router)
print("[OK] natacha chat router enabled")

# Health / Liveness
from routes import health_route
app.include_router(health_route.router)

@app.get("/__alive", tags=["system"])
async def alive():
    return {
        "status": "alive",
        "service": "natacha-api",
        "engine": "natacha-unified",
    }

# Context & Memory
from routes.context_unified import router as context_unified_router
from routes.memory_unified import router as memory_unified_router
app.include_router(memory_unified_router)
app.include_router(context_unified_router)

# Agent interaction
from ops.agent.interact import router as agent_router
app.include_router(agent_router)

# Manifests / Debug FS / OpenAI
from ops.system.manifests import router as manifests_router
from routes.debug_openai import router as debug_openai_router
from routes.debug_fs import router as debug_fs_router

app.include_router(manifests_router)
app.include_router(debug_openai_router)
app.include_router(debug_fs_router)

# ================================================================
# 4) OS / SYSTEM ROUTERS (CANÓNICOS)
# ================================================================

# --- User live cognitive state (READ ONLY)
try:
    from routes.ops_self import router as ops_self_router
    app.include_router(ops_self_router)
    print("[OK] ops_self router enabled")
except Exception as e:
    print(f"[SKIP] ops_self router: {e}")

# --- System state
try:
    from routes.system_state import router as system_state_router
    app.include_router(system_state_router)
    print("[OK] system_state router enabled")
except Exception as e:
    print(f"[SKIP] system_state router: {e}")

# --- System diagnose
try:
    from routes.system_diagnose import router as system_diagnose_router
    app.include_router(system_diagnose_router)
    print("[OK] system_diagnose router enabled")
except Exception as e:
    print(f"[SKIP] system_diagnose router: {e}")

# --- System decision (SAFE)
try:
    from routes.system_decide import router as system_decide_router
    app.include_router(system_decide_router)
    print("[OK] system_decide router enabled")
except Exception as e:
    print(f"[SKIP] system_decide router: {e}")

# --- System self model (READ ONLY)
try:
    from routes.system_self import router as system_self_router
    app.include_router(system_self_router)
    print("[OK] system_self router enabled")
except Exception as e:
    print(f"[SKIP] system_self router: {e}")

# ================================================================
# 5) SEMANTIC DEBUG (PASIVO)
# ================================================================

try:
    from ops.semantic.routes import router as semantic_router
    app.include_router(semantic_router)
    print("[OK] semantic debug router enabled")
except Exception as e:
    print(f"[SKIP] semantic router: {e}")

# ================================================================
# 6) TASKS
# ================================================================

try:
    from routes.tasks_routes import router as tasks_router
    app.include_router(tasks_router)
    print("[OK] tasks router enabled")
except Exception as e:
    print(f"[SKIP] tasks router: {e}")

# ================================================================
# 7) OPTIONAL MODULES (FAST BOOT SAFE)
# ================================================================

def safe_include(module_name: str):
    try:
        module = __import__(module_name, fromlist=["router"])
        router = getattr(module, "router", None)
        if router:
            app.include_router(router)
            print(f"[OK] Included: {module_name}")
    except Exception as e:
        print(f"[SKIP] {module_name} – {e}")

if os.getenv("NATACHA_FAST_BOOT") != "1":
    safe_include("ops.extensions.core_bridge_ext")
    safe_include("ops.affective_train")
    safe_include("ops.cognitive_evolution")
    safe_include("ops.introspection.code_scan")
    safe_include("ops.introspection.history_reader")
    safe_include("ops.introspection.self_reflect")
    safe_include("ops.introspection.meta_reflect")
    safe_include("ops.self_diagnostics")
    safe_include("ops.firestore_adapter")

print("[INFO] Legacy memory routes DISABLED (A2 clean)")

# ================================================================
# 8) ROOT
# ================================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "natacha-unified-v20.6-fast-boot",
        "message": "Natacha API – Cloud Run FAST BOOT ready 🚀"
    }

# ================================================================
# 9) OPENAPI
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="CEREBRO-v1-FROZEN",
        description="Natacha internal API (fast boot)",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"},
        {"url": "http://localhost:8080"},
    ]

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

# ================================================================
# 10) STARTUP
# ================================================================

@app.on_event("startup")
def on_startup():
    start_background(load_memory_from_gcs)
    start_background(wait_and_reset_memory_index)

    try:
        from ops.startup.post_startup import launch_post_startup
        start_background(launch_post_startup)
        print("[STARTUP] post_startup launched in background")
    except Exception as e:
        print(f"[STARTUP][SKIP] post_startup unavailable: {e}")

    print("[STARTUP] Fast boot startup completed")
