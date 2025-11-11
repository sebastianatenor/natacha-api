import os, importlib.util, sys

# Ruta del app.py en la raíz del repo dentro del contenedor (/app)
APP_FILE = os.path.join(os.path.dirname(__file__), "app.py")

if not os.path.exists(APP_FILE):
    # Fallback: si no existe app.py, intentar paquete app/ con __init__.py que exponga `app`
    try:
        from app import app  # noqa: F401
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

try:
    from routes.ops_self import router as ops_self_router
    app.include_router(ops_self_router)
except ModuleNotFoundError:
    pass


try:
    from routes.actions_routes import router as actions_routes_router
    app.include_router(actions_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.auto_routes import router as auto_routes_router
    app.include_router(auto_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.cog_routes import router as cog_routes_router
    app.include_router(cog_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.core_routes import router as core_routes_router
    app.include_router(core_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.embeddings_routes import router as embeddings_routes_router
    app.include_router(embeddings_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.health_ext import router as health_ext_router
    app.include_router(health_ext_router)
except ModuleNotFoundError:
    pass


try:
    from routes.health_route import router as health_route_router
    app.include_router(health_route_router)
except ModuleNotFoundError:
    pass


try:
    from routes.health_routes import router as health_routes_router
    app.include_router(health_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.memory_routes import router as memory_routes_router
    app.include_router(memory_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.memory_v2 import router as memory_v2_router
    app.include_router(memory_v2_router)
except ModuleNotFoundError:
    pass


try:
    from routes.openapi_compat import router as openapi_compat_router
    app.include_router(openapi_compat_router)
except ModuleNotFoundError:
    pass


try:
    from routes.ops_routes import router as ops_routes_router
    app.include_router(ops_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.semantic_routes import router as semantic_routes_router
    app.include_router(semantic_routes_router)
except ModuleNotFoundError:
    pass


try:
    from routes.tasks_routes import router as tasks_routes_router
    app.include_router(tasks_routes_router)
except ModuleNotFoundError:
    pass

