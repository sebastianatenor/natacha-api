import os
import sys
import json
import importlib.util
from pathlib import Path

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

# ================================================================
# Cargar app.py desde la raíz del repo dentro del contenedor
# ================================================================

APP_FILE = os.path.join(os.path.dirname(__file__), "app.py")

if not os.path.exists(APP_FILE):
    # Fallback: intentar paquete "app"
    try:
        from app import app  # noqa
    except Exception as e:
        raise RuntimeError(f"No se encontró app.py ni paquete app con `app`: {e}")
else:
    spec = importlib.util.spec_from_file_location("natacha_root_app", APP_FILE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["natacha_root_app"] = mod
    spec.loader.exec_module(mod)  # type: ignore
    app = getattr(mod, "app", None)
    if app is None:
        raise RuntimeError("app.py existe pero no define variable `app`")

# ================================================================
# IMPORTAR Y REGISTRAR ROUTERS (SAFE MODE)
# ================================================================

def safe_include(module_path: str):
    """Incluye routers sin romper el arranque si falta alguno."""
    try:
        module = __import__(module_path, fromlist=["router"])
        router = getattr(module, "router", None)
        if router is not None:
            app.include_router(router)
    except ModuleNotFoundError:
        pass


safe_include("routes.ops_self")
safe_include("routes.actions_routes")
safe_include("routes.auto_routes")
safe_include("routes.cog_routes")
safe_include("routes.core_routes")
safe_include("routes.embeddings_routes")
safe_include("routes.health_ext")
safe_include("routes.health_route")
safe_include("routes.health_routes")
safe_include("routes.memory_routes")
safe_include("routes.memory_v2")
safe_include("routes.memory_engine_routes")
safe_include("routes.natacha_routes")
safe_include("routes.actions_openapi")  # ⬅️ esquema reducido para Actions
safe_include("routes.openapi_compat")
safe_include("routes.ops_routes")
safe_include("routes.semantic_routes")
safe_include("routes.tasks_routes")

# memory v1 explícito (si existe)
try:
    from app.api_v1.memory_v1_routes import router as memory_v1_router
    app.include_router(memory_v1_router)
except Exception:
    pass

# ================================================================
# ENDPOINT OPENAPI PÚBLICO PARA CHATGPT
# ================================================================

@app.get("/openapi_public.json", include_in_schema=False)
def openapi_public():
    """
    Devuelve la especificación pública reducida para ChatGPT Actions.
    """
    base_dir = Path(__file__).parent
    path = base_dir / "public_openapi.json"

    if not path.exists():
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Natacha Public API (missing file)",
                "version": "1.0.0",
                "description": "public_openapi.json no encontrado en el contenedor."
            },
            "paths": {}
        }

    with path.open() as f:
        return json.load(f)

# ================================================================
# CUSTOM OPENAPI (INTERNO)
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=getattr(app, "title", "Natacha API"),
        version="1.0.0",
        description="Natacha API – runtime schema",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"}
    ]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
