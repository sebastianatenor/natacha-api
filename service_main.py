from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib, traceback

app = FastAPI(title="Natacha API", version="1.0.0")

# CORS amplio (ajustá si querés restringir)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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

# Montar routers opcionales si existen (no rompe si faltan)
IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}

# Hook OpenAPI para inyectar 'servers' desde OPENAPI_PUBLIC_URL
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

# Exponer /openapi.v1.json compatible
try:
    from routes.openapi_compat import router as openapi_router
    app.include_router(openapi_router)
except Exception:
    pass
