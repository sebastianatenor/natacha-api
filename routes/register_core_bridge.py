from service_main import app
from routes import core_bridge_routes

app.include_router(core_bridge_routes.router)
print("[INIT] 🔗 Router /core activado dinámicamente")
