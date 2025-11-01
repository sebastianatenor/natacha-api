import json
from datetime import datetime
import requests

def _fetch(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def load_operational_context(api_base="http://127.0.0.1:8002", limit=20):
    """
    Intenta leer primero /ops/insights y si no existe
    cae a /ops/summary. Guarda el resultado en last_context.json.
    """
    insights_url = f"{api_base}/ops/insights?limit={limit}"
    summary_url = f"{api_base}/ops/summary?limit={limit}"

    data = None
    used_url = None

    # 1) intento insights
    try:
        data = _fetch(insights_url)
        used_url = insights_url
    except Exception as e:
        print(f"⚠️ /ops/insights no disponible ({e}), probando /ops/summary ...")
        # 2) intento summary
        try:
            data = _fetch(summary_url)
            used_url = summary_url
        except Exception as e2:
            print(f"❌ No se pudo cargar contexto operativo desde {api_base}: {e2}")
            return None

    payload = {
        "loaded_at": datetime.utcnow().isoformat(),
        "source": used_url,
        "data": data,
    }
    with open("last_context.json", "w") as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Contexto operativo cargado desde {used_url}")
    return data
