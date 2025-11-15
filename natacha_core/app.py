from fastapi import FastAPI
from routes.affective_map import router as affective_router

app = FastAPI(
    title="Natacha Core",
    version="16.1-modular",
    description="Motor afectivo modular con endpoints integrados."
)

# Registrar módulos de rutas
app.include_router(affective_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Natacha Core operativo 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
app.include_router(affective_projection.router)
