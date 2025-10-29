from fastapi import FastAPI
import httpx

app = FastAPI()
TARGET = "http://127.0.0.1:8000"  # health-monitor local

@app.get("/infra_history_cloud")
async def infra_history_cloud():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{TARGET}/infra_history", timeout=5)
    return r.json()

@app.get("/")
def root():
    return {"ok": True, "proxy": "infra_history_cloud -> infra_history"}
