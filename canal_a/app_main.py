from fastapi import FastAPI
from routes import ctx_routes
from routes import ops_routes

app = FastAPI(title="natacha-api-a")
app.include_router(ctx_routes.router)
app.include_router(ops_routes.router)

@app.get("/__alive")
def alive():
    return {"ok": True, "app": "canal-a"}
