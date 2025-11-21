# ============================================================
# LEGACY MODULE – NO USAR COMO ENTRYPOINT
# El core bridge oficial se monta desde `service_main:app`
# vía `safe_include("routes.core_bridge")` y
# `safe_include("ops.extensions.core_bridge_ext")`.
# Este archivo se mantiene solo como histórico.
# ============================================================

from service_main import app
from routes import core_bridge_routes

app.include_router(core_bridge_routes.router)
print("[INIT] 🔗 Router /core activado dinámicamente")
