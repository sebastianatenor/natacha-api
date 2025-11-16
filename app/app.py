from fastapi import FastAPI
from routes import core_bridge

app = FastAPI(
    title="Natacha API",
    version="18.2-core-bridge",
    description="Bridge entre Natacha API y Natacha Core"
)

# ✅ Registrar el nuevo router
app.include_router(core_bridge.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "API principal activa 🚀"}
