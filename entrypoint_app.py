from fastapi import FastAPI
from routes import openapi_compat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib, traceback

app = FastAPI(title="Natacha API (entrypoint)")
app.include_router(openapi_compat.router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/__alive")
def __alive():
    return {"ok": True, "where": "entrypoint_app", "cwd": os.getcwd()}

@app.get("/__sha")
def __sha():
    try:
        with open(__file__, "rb") as fh:
            return {"file": __file__, "sha256": hashlib.sha256(fh.read()).hexdigest()}
    except Exception as e:
        return {"error": str(e)}

IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}

# === OpenAPI servers override (entrypoint) ===
def custom_openapi():
    public_url = os.environ.get("OPENAPI_PUBLIC_URL", "").rstrip("/")
    schema = get_openapi(
        title=getattr(app, "title", "Natacha API"),
        version=getattr(app, "version", "1.0.0"),
        description=getattr(app, "description", "Natacha Cloud API"),
        routes=app.routes,
    )
    if public_url:
        schema["servers"] = [{"url": public_url}]
    return schema

try:
    app.openapi_schema = None  # limpiar cache si estaba generado
except Exception:
    pass
app.openapi = custom_openapi