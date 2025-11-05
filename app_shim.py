from fastapi import FastAPI

# 1) Obtener la app real desde service_main, sea instancia o factory
_real = None
try:
    from service_main import app as _maybe
    _real = _maybe() if callable(_maybe) else _maybe
except Exception as e:
    print("WARN app_shim: no pude importar 'app' de service_main:", e)

# 2) Si no logramos una instancia, crear una base para no romper
app = _real if isinstance(_real, FastAPI) else FastAPI(title="natacha-shim")

# 3) Cablear routers nuevos y también el /context/ existente para mantener compatibilidad
try:
    from routes import ctx_routes, ops_routes
    app.include_router(ctx_routes.router)
    app.include_router(ops_routes.router)
except Exception as e:
    print("WARN app_shim: wiring ctx/ops falló:", e)

# 4) Intentar incluir el router legacy /context/* si existe
try:
    from routes import context_routes
    if getattr(context_routes, "router", None):
        app.include_router(context_routes.router)
except Exception as e:
    print("WARN app_shim: wiring context legacy falló:", e)
