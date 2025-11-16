from fastapi import FastAPI
from routes import affective_map, affective_projection, affective_timeline

app = FastAPI(
    title="Natacha Core",
    version="19.0-affective-timeline",
    description="Core API con proyección cognitivo-afectiva, timeline emocional y mapa adaptativo."
)

# Routers principales
app.include_router(affective_map.router)
app.include_router(affective_projection.router)
app.include_router(affective_timeline.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Natacha Core activo 🚀"}
