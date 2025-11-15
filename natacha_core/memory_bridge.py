import os
import requests

MEMORY_API_URL = os.getenv("MEMORY_API_URL", "http://localhost:8080/memory/v2")

def store_memory(user: str, text: str, tags: list[str] = None):
    """Guarda una nueva memoria contextual asociada al usuario."""
    payload = {
        "items": [{
            "text": text,
            "tags": tags or ["core-context"],
        }]
    }
    try:
        r = requests.post(f"{MEMORY_API_URL}/store", json=payload, timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

def retrieve_context(limit: int = 5):
    """Obtiene los recuerdos más recientes del sistema para análisis contextual."""
    try:
        r = requests.get(f"{MEMORY_API_URL}/ops/memory-info", timeout=5)
        data = r.json()
        if "error" in data:
            return {"status": "empty", "context": []}
        return data
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}
