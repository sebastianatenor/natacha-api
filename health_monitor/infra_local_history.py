import os
import json
from datetime import datetime

# 🔹 Nuevo destino seguro (usa /tmp en vez de /app)
HISTORY_FILE = os.environ.get("INFRA_HISTORY_PATH", "/tmp/infra_history.json")

def ensure_history_dir():
    """Crea la carpeta de logs si no existe."""
    directory = os.path.dirname(HISTORY_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def load_history():
    """Carga el historial local si existe, o retorna una lista vacía."""
    ensure_history_dir()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_entry(data: dict):
    """Agrega una nueva entrada al historial local."""
    ensure_history_dir()
    history = load_history()
    data["timestamp"] = data.get("timestamp") or datetime.utcnow().isoformat()
    history.append(data)
    # Mantener máximo 100 registros
    history = history[-100:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    return data

def get_history():
    """Devuelve todo el historial local."""
    return load_history()

def clear_history():
    """Vacía el historial local."""
    ensure_history_dir()
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
    return True
