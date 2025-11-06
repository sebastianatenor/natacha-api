from routes.health_routes import router as health_router
from routes.cog_routes import router as cog_router
from routes.actions_routes import router as actions_router
from routes.tasks_routes import router as tasks_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib, traceback
from routes.auto_routes import router as auto_router

app = FastAPI()
app.include_router(health_router)
app.include_router(cog_router)
app.include_router(actions_router)

app.include_router(tasks_router)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auto_router)

@app.get("/__alive")
def __alive():
    return {"ok": True, "where": "service_main", "cwd": os.getcwd()}

@app.get("/__sha")
def __sha():
    try:
        with open(__file__, "rb") as fh:
            return {"file": __file__, "sha256": hashlib.sha256(fh.read()).hexdigest()}
    except Exception as e:
        return {"error": str(e)}

# Routers opcionales (no rompe si faltan)
IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, routes=app.routes, description="Natacha API")
    public = os.getenv("OPENAPI_PUBLIC_URL","").rstrip("/")
    if public:
        schema["servers"] = [{"url": public}]
    schema["openapi"] = "3.1.0"
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi_schema = None
app.openapi = custom_openapi

# /openapi.v1.json compat
try:
    from routes.openapi_compat import router as openapi_router
    app.include_router(openapi_router)
except Exception:
    pass
# --- Health at root (idempotente) ---
try:
    app
except NameError:
    from fastapi import FastAPI
#     app = FastAPI()  # DUPLICATE REMOVED

@app.get("/health", include_in_schema=False)
def _health():
    return {"status": "ok"}

# --- FINAL fallback health (direct on app) ---
try:
    app
except NameError:
    from fastapi import FastAPI
#     app = FastAPI()  # DUPLICATE REMOVED

@app.get("/health", include_in_schema=False)
def health_final():
    return {"status": "ok (fallback)"}

# --- Canonical /health (must be after final app assignment) ---
try:
    app
except NameError:
    from fastapi import FastAPI
#     app = FastAPI()  # DUPLICATE REMOVED

@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}

# === Debug: saber desde dónde corre Uvicorn y qué rutas hay ===
from fastapi import APIRouter
_debug_router = APIRouter()

@_debug_router.get("/__whoami", include_in_schema=False)
def __whoami():
    import inspect
    return {
        "module": __name__,
        "file": __file__,
        "app_type": str(type(app)),
        "routes_count": len(app.router.routes),
    }

@_debug_router.get("/__routes", include_in_schema=False)
def __routes():
    return [getattr(r, "path", str(r)) for r in app.router.routes]

app.include_router(_debug_router)

# ---- canonical health endpoint (direct on main app) ----
try:
    from fastapi import HTTPException
    @app.get("/health", include_in_schema=False)
    def _health():
        # keep it super light & deterministic
        return {"status": "ok", "source": "service_main"}
except Exception as e:
    # If something odd happens during import, fail visibly in logs
    print("WARN: could not register /health on service_main:", e)
# === injected diagnostics: health + route dump (idempotent) ===
try:
    from fastapi import APIRouter
    _diag = APIRouter()

    @_diag.get("/__routes2", include_in_schema=False)
    def __routes2():
        # listar paths para confirmar que /health existe
        return [getattr(r, "path", str(r)) for r in app.router.routes]

    @_diag.get("/health", include_in_schema=False)
    def __health_main():
        return {"status": "ok", "source": "service_main.inj"}

    app.include_router(_diag)
except Exception as _e:
    print("WARN inject diag failed:", _e)
