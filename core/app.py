from datetime import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Core local funcionando correctamente 🚀",
        "timestamp": datetime.utcnow().isoformat(),
    }
