from fastapi import FastAPI
from routes import affective_map, affective_projection, affective_timeline, affective_sync

app = FastAPI(
    title="Natacha Core",
    version="18.0-affective-projection",
    description="Core API con proyección cognitivo-afectiva, timeline y sincronización adaptativa."
)

# Routers principales
app.include_router(affective_map.router)
app.include_router(affective_projection.router)
app.include_router(affective_timeline.router)
app.include_router(affective_sync.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Natacha Core activo 🚀"}
