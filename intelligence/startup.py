import json
from datetime import datetime
import requests

def load_operational_context(api_base="http://127.0.0.1:8002", limit=20):
    """
    Descarga el estado operativo desde /ops/insights y lo guarda localmente.
    No rompe si falla.
    """
    url = f"{api_base}/ops/insights?limit={limit}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        payload = {
            "loaded_at": datetime.utcnow().isoformat(),
            "source": url,
            "data": data,
        }
        with open("last_context.json", "w") as f:
            json.dump(payload, f, indent=2)
        print(f"✅ Contexto operativo cargado desde {url}")
        return data
    except Exception as e:
        print(f"⚠️ No se pudo cargar contexto operativo desde {url}: {e}")
        return None
