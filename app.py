from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
import os, hashlib, traceback

app = FastAPI(title="Natacha API", version="1.0.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # si querés, restringí tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints base/health ---
@app.get("/__alive")
def __alive():
    return {"ok": True, "where": "app", "cwd": os.getcwd()}

@app.get("/__sha")
def __sha():
    try:
        with open(__file__, "rb") as fh:
            return {"file": __file__, "sha256": hashlib.sha256(fh.read()).hexdigest()}
    except Exception as e:
        return {"error": str(e)}

# Intento de importar routers opcionales
IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}

# --- Hook OpenAPI con 'servers' ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description="Natacha unified API",
    )
    public_url = os.getenv("OPENAPI_PUBLIC_URL", "").strip()
    if public_url:
        schema["servers"] = [{"url": public_url}]
    app.openapi_schema = schema
    return app.openapi_schema

# limpiar cache y enganchar el hook
try:
    app.openapi_schema = None
except Exception:
    pass
app.openapi = custom_openapi
