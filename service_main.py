import os
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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


def safe_include(app, import_fn, name: str):
    """
    Importa e incluye routers de forma segura.
    Si falla, el sistema sigue vivo.
    """
    try:
        router = import_fn()
        app.include_router(router)
        print(f"[ROUTER] loaded: {name}")
    except Exception as e:
        print(f"[ROUTER][SKIPPED] {name}: {e}")


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
    try:
        if os.getenv("K_SERVICE") is None:
            print("[MEMORY] Local run detected, bootstrap skipped")
            return

        local_path = Path(os.getenv("NATACHA_MEMORY_LOCAL"))

        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")

        if blob.exists():
            blob.download_to_filename(local_path)
            print("[MEMORY] Canonical memory restored from GCS")
        else:
            local_path.touch(exist_ok=True)
            print("[MEMORY] Empty memory initialized")

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
# CORE ROUTERS (DEBEN EXISTIR)
# ================================================================
from routes.health import router as health_router
from routes.get_system_state import router as get_system_state_router

app.include_router(health_router)
app.include_router(get_system_state_router)

print("[ROUTER] core loaded")

# ================================================================
# OPTIONAL / EVOLUTIVE ROUTERS (AISLADOS)
# ================================================================
def load_optional_routers():

    safe_include(
        app,
        lambda: __import__("routes.system_daily_snapshot", fromlist=["router"]).router,
        "system_daily_snapshot",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_force_checkpoint", fromlist=["router"]).router,
        "system_force_checkpoint",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_diagnose", fromlist=["router"]).router,
        "system_diagnose",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_narrative", fromlist=["router"]).router,
        "system_narrative",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_memory_diagnostic_v2", fromlist=["router"]).router,
        "memory_diagnostic_v2",
    )

    safe_include(
        app,
        lambda: __import__("routes.memory_recent", fromlist=["router"]).router,
        "memory_recent",
    )

    safe_include(
        app,
        lambda: __import__("routes.memory_recall", fromlist=["router"]).router,
        "memory_recall",
    )

    safe_include(
        app,
        lambda: __import__("routes.memory_note", fromlist=["router"]).router,
        "memory_note",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_state.router", fromlist=["router"]).router,
        "system_state",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_perception.router", fromlist=["router"]).router,
        "system_perception",
    )

    # ⚠️ ESTE ES EL QUE ESTABA ROMPIENDO TODO
    safe_include(
        app,
        lambda: __import__("routes.memory_index", fromlist=["router"]).router,
        "memory_index",
    )

    safe_include(
        app,
        lambda: __import__("ops.agent.interact", fromlist=["router"]).router,
        "agent_interact",
    )

    safe_include(
        app,
        lambda: __import__("routes.natacha_routes", fromlist=["router"]).router,
        "natacha_routes",
    )

    safe_include(
        app,
        lambda: __import__("ops.timeline.router", fromlist=["router"]).router,
        "timeline",
    )

    safe_include(
        app,
        lambda: __import__("ops.symbolic.router", fromlist=["router"]).router,
        "symbolic",
    )

    safe_include(
        app,
        lambda: __import__("ops.semantic.routes", fromlist=["router"]).router,
        "semantic",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_baseline.router", fromlist=["router"]).router,
        "system_baseline",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_self_repair.router", fromlist=["router"]).router,
        "system_self_repair",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_full_status", fromlist=["router"]).router,
        "system_full_status",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_proposals", fromlist=["router"]).router,
        "system_proposals",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_generate_proposal", fromlist=["router"]).router,
        "system_generate_proposal",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_signals", fromlist=["router"]).router,
        "system_signals",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_proposal_lifecycle", fromlist=["router"]).router,
        "system_proposal_lifecycle",
    )

    safe_include(
        app,
        lambda: __import__("routes.system_decisions", fromlist=["router"]).router,
        "system_decisions",
    )

# ================================================================
# DEBUG (NO CRÍTICO)
# ================================================================
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
    bootstrap_memory()
    load_optional_routers()

    try:
        from ops.startup.post_startup import launch_post_startup
        start_background(launch_post_startup)
        print("[STARTUP] post_startup launched")
    except Exception as e:
        print(f"[STARTUP][WARN] post_startup skipped: {e}")

    try:
        from ops.cognitive.startup_self_repair import attempt_startup_self_repair
        attempt_startup_self_repair()
        print("[STARTUP] startup self-repair evaluated")
    except Exception as e:
        print(f"[STARTUP][WARN] self-repair skipped: {e}")

    # 🧠 B5 — Cognitive Supervisor (auto-repair proposal loop)
    try:
        from ops.cognitive.supervisor import supervisor_loop
        start_background(supervisor_loop)
        print("[SUPERVISOR] cognitive supervisor running")
    except Exception as e:
        print(f"[SUPERVISOR][WARN] not started: {e}")

    print("[STARTUP] baseline ready")

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
