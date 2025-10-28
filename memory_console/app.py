from fastapi import FastAPI
from google.cloud import firestore
import os

app = FastAPI(title="Natacha Memory Console", version="1.0")

# ✅ Health check
@app.get("/health")
def health():
    """Chequea si Firestore está accesible."""
    try:
        db = firestore.Client()
        db.collections()  # simple test
        return {"health": "good", "firestore": True}
    except Exception as e:
        return {"health": "bad", "firestore": False, "error": str(e)}


# ✅ Endpoint principal: guarda en memoria
@app.post("/memory/store")
def store_memory(data: dict):
    """Guarda un valor en Firestore en la colección 'memories'."""
    try:
        db = firestore.Client()
        key = data.get("key")
        value = data.get("value")
        if not key:
            return {"error": "Missing 'key' in request"}
        db.collection("memories").document(key).set(data)
        return {"stored": True, "key": key, "value": value}
    except Exception as e:
        return {"stored": False, "error": str(e)}


# ✅ Endpoint: obtiene una memoria por clave
@app.get("/memory/get/{key}")
def get_memory(key: str):
    """Recupera un documento de Firestore por clave."""
    try:
        db = firestore.Client()
        doc = db.collection("memories").document(key).get()
        if doc.exists:
            return {"found": True, "key": key, "value": doc.to_dict().get("value"), "source": "firestore"}
        else:
            return {"found": False, "key": key}
    except Exception as e:
        return {"error": str(e)}


# ✅ Nuevo endpoint: listar documentos de Firestore
@app.get("/firestore/list")
def list_firestore_documents():
    """Devuelve todos los documentos de la colección 'memories'."""
    try:
        db = firestore.Client()
        docs = db.collection("memories").stream()
        data = [{doc.id: doc.to_dict()} for doc in docs]
        return {
            "count": len(data),
            "documents": data
        }
    except Exception as e:
        return {"error": str(e)}


# ✅ Configuración adicional: path de credenciales
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "/app/secrets/service-account.json"
)
