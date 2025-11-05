
# === wired_by_natacha ===
try:
    from routes import ctx_routes, ops_routes
except Exception as e:
    ctx_routes = None
    ops_routes = None
    print('WARN routes import failed:', e)
from routes import ops_routes, context2_routes
# MARK service_main ctx2 enabled
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_open
def _wire_extra_routes(_app):
    try:
        if ctx_routes:
            _app.include_router(ctx_routes.router)
        if ops_routes:
            _app.include_router(ops_routes.router)
    except Exception as _e:
        print('WARN include routers:', _e)


_wire_extra_routes(app)
api
import os, hashlib

from routes.context_routes import router as ctx_router
from routes.context2_routes import router as ctx2_router

app = FastAPI(title="Natacha API", version="1.0.0")

# === explicit wire by plan F2 ===
try:
    from routes import ctx_routes, ops_routes
    app.include_router(ctx_routes.router)
    app.include_router(ops_routes.router)
    print('WIRE: ctx_routes & ops_routes incluidos en app')
except Exception as e:
    print('WIRE ERROR:', e)


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


# === auto_wire_by_natacha ===
try:
    from routes import ctx_routes, ops_routes
    from fastapi import FastAPI
    _routers = []
    for _mod in (ctx_routes, ops_routes):
        try:
            _r = getattr(_mod, "router", None)
            if _r:
                _routers.append(_r)
        except Exception as _e:
            print("WARN getting router:", _e)

    # Cablear a cualquier instancia FastAPI global ya creada
    try:
        for _name, _obj in list(globals().items()):
            if isinstance(_obj, FastAPI):
                for _r in _routers:
                    try:
                        _obj.include_router(_r)
                    except Exception as _e:
                        print("WARN include (global scan):", _e)
    except Exception as _e:
        print("WARN global scan:", _e)

    # Si hay factories, intentamos enganchar antes del return app
    def _inject_in_factory(code):
        return re.sub(
            r"(def\s+(create_app|get_app)\s*\([^)]*\)\s*:\s*.*?\breturn\s+app)",
            r"\1\n    try:\n        "
            r"\n        # auto-wire in factory\n"
            r"        from routes import ctx_routes as _ctxr, ops_routes as _opsr\n"
            r"        for _r in [getattr(_ctxr,'router',None), getattr(_opsr,'router',None)]:\n"
            r"            if _r: app.include_router(_r)\n"
            r"    except Exception as _e:\n        print('WARN factory wire:', _e)",
            code, flags=re.S
        )
    try:
        _new = _inject_in_factory("")
    except Exception:
        pass
except Exception as e:
    print("WARN auto-wire failed:", e)

