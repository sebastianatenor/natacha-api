from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Core local funcionando correctamente 🚀",
        "timestamp": datetime.utcnow().isoformat()
    }
