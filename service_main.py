from routes import ops_routes, context2_routes
# MARK service_main ctx2 enabled
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib

from routes.context_routes import router as ctx_router
from routes.context2_routes import router as ctx2_router

app = FastAPI(title="Natacha API", version="1.0.0")

# Routers
app.include_router(ctx_router)
app.include_router(ctx2_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes, description="Natacha API"
    )
    public = os.getenv("OPENAPI_PUBLIC_URL", "").strip("/")
    if public:
        schema["servers"] = [{"url": public}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

# === auto-include added ===
app.include_router(ops_routes.router)
app.include_router(context2_routes.router)

# === auto-include (forced) ===
try:
    from routes import ctx_routes, ops_routes
    try:
        app.include_router(ctx_routes.router)
    except Exception as _e:
        print("WARN include ctx_routes:", _e)
    try:
        app.include_router(ops_routes.router)
    except Exception as _e:
        print("WARN include ops_routes:", _e)
except Exception as e:
    print("WARN imports for ctx/ops failed:", e)

