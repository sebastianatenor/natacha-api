from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import json
import datetime
import requests

app = FastAPI(
    title="Natacha Core Service",
    description="Servicio central de procesamiento cognitivo de Natacha 🧠",
    version="1.0.0",
)

# === MODELOS ===
class ProcessInput(BaseModel):
    text: str
    user: str | None = None
    metadata: dict | None = None


# === ENDPOINTS BASE ===
@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Core local funcionando correctamente 🚀",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }


# === ENDPOINT /process ===
@app.post("/process")
def process(input_data: ProcessInput):
    """Simula procesamiento cognitivo básico"""
    text = input_data.text.lower()
    response = {}

    # Ejemplo simple de interpretación
    if "hola" in text:
        response["intent"] = "greeting"
        response["reply"] = "¡Hola! Soy Natacha Core. ¿En qué puedo ayudarte?"
    elif "estado" in text or "status" in text:
        response["intent"] = "system_status"
        response["reply"] = "Todo el ecosistema Natacha está estable y sincronizado 💾⚙️"
    else:
        response["intent"] = "unknown"
        response["reply"] = "No estoy segura de qué quisiste decir 🤔"

    # Registrar evento en memory-console
    try:
        payload = {
            "key": f"core_log_{datetime.datetime.utcnow().isoformat()}",
            "value": json.dumps({
                "input": input_data.text,
                "intent": response["intent"],
                "reply": response["reply"],
                "user": input_data.user,
                "metadata": input_data.metadata
            })
        }
        requests.post("http://natacha-memory-console:8080/memory/store", json=payload, timeout=3)
    except Exception as e:
        response["memory_sync"] = f"⚠️ Error al registrar en memoria: {e}"

    return {
        "core_status": "ok",
        "input": input_data.text,
        "response": response
    }


# === ENDPOINT /analyze ===
@app.post("/analyze")
def analyze(input_data: ProcessInput):
    """Análisis básico de texto"""
    text = input_data.text

    analysis = {
        "length": len(text),
        "words": len(text.split()),
        "has_question": "?" in text,
        "has_greeting": any(w in text.lower() for w in ["hola", "buenos días", "hey"]),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        "analysis_status": "ok",
        "text": text,
        "analysis": analysis
    }


# === MAIN ===
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
