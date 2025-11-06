from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from canal_a.routes import ctx_routes, ops_routes
import os

API_KEY = os.getenv("NATACHA_API_KEY", "dev-key")
app = FastAPI(title="natacha-api-a")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.middleware("http")
async def key_guard(request: Request, call_next):
    if request.method in ("POST","PATCH","DELETE"):
        if request.headers.get("x-api-key") != API_KEY:
            from starlette.responses import JSONResponse
            return JSONResponse({"ok": False, "error": "invalid API key"}, status_code=401)
    return await call_next(request)

app.include_router(ctx_routes.router)
app.include_router(ops_routes.router)


from fastapi import APIRouter
import sys, inspect
from canal_a.routes import ops_routes as _ops_mod, ctx_routes as _ctx_mod

diag = APIRouter(prefix="/ops", tags=["ops"])

@diag.get("/routes_dump")
def routes_dump():
    return {
        "count": len(app.routes),
        "paths": sorted([getattr(r, "path", str(r)) for r in app.routes]),
    }

@diag.get("/whoami")
def whoami():
    return {
        "sys_path": sys.path,
        "ops_routes_file": inspect.getsourcefile(_ops_mod),
        "ctx_routes_file": inspect.getsourcefile(_ctx_mod),
        "uvicorn_app": str(app.title),
    }

app.include_router(diag)


from importlib.metadata import version as _pkg_version
import os, sys, json, platform
from datetime import datetime

@app.get("/ops/version", tags=["ops"])
def ops_version():
    # build_stamp si existe (lo copiamos al contenedor como /app/.build_stamp)
    stamp = None
    try:
        with open("/app/.build_stamp","r") as f:
            stamp = f.read().strip()
    except Exception:
        pass

    pkgs = {}
    for name in ("fastapi","uvicorn","google-cloud-firestore","google-auth","requests"):
        try:
            pkgs[name] = _pkg_version(name)
        except Exception:
            pkgs[name] = None

    return {
        "ok": True,
        "service": os.getenv("K_SERVICE","unknown"),
        "revision": os.getenv("K_REVISION","unknown"),
        "stamp": stamp,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": pkgs,
        "utc": datetime.utcnow().isoformat() + "Z",
    }

