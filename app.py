from fastapi import FastAPI
from routes import ops, memory_routes  # 👈 Asegurate de incluir memory_routes

app = FastAPI()

# Registrar los routers
app.include_router(ops.router)
app.include_router(memory_routes.router)  # 👈 Muy importante

@app.get("/health")
def health():
    return {"status": "ok", "message": "Natacha API base funcionando correctamente 🚀"}
