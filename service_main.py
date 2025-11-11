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

from routes.ops_self import router as ops_self_router
app.include_router(ops_self_router)
