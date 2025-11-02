import json
from datetime import datetime
import os
import requests
from pathlib import Path


def _fetch(url: str):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def load_operational_context(api_base: str = "http://127.0.0.1:8002", limit: int = 20):
    """
    Intenta leer primero /ops/insights y si no existe
    cae a /ops/summary. Guarda el resultado en last_context.json
    y deja un log de arranques en logs/boot_history.jsonl.
    Además: si detecta tareas duplicadas en la respuesta,
    crea una memoria automática en la API de Natacha.
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

    # armamos el payload que vamos a guardar
    payload = {
        "loaded_at": datetime.utcnow().isoformat(),
        "source": used_url,
        "data": data,
    }

    # 1) guardar el contexto en disco
    with open("last_context.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    # 2) guardar historial de arranques
    try:
        logdir = Path("logs")
        logdir.mkdir(exist_ok=True)
        logfile = logdir / "boot_history.jsonl"

        # si la API devolvió projects (caso /ops/insights)
        projects = None
        raw_counts = None
        if isinstance(data, dict):
            if "projects" in data and isinstance(data["projects"], list):
                projects = [p.get("name") for p in data["projects"]]
            if "raw" in data and isinstance(data["raw"], dict):
                raw_counts = data["raw"]

        entry = {
            "loaded_at": payload["loaded_at"],
            "source": payload["source"],
            "projects": projects,
            "raw_counts": raw_counts,
        }
        with logfile.open("a", encoding="utf-8") as lf:
            lf.write(json.dumps(entry) + "\n")

    except Exception as e:
        print(f"⚠️ No pude escribir logs/boot_history.jsonl: {e}")

    # 3) auto-memo de duplicados (inteligencia mínima en el arranque)
    try:
        duplicates = []
        if isinstance(data, dict):
            duplicates = data.get("duplicates") or []

        if duplicates:
            # armamos un resumen corto para la memoria
            titles = [f"{d.get('title')} ({d.get('count')})" for d in duplicates]
            msg = "Tareas duplicadas detectadas al arrancar: " + "; ".join(titles)

            nat_api = os.getenv("NATACHA_CONTEXT_API") or api_base
            mem_url = f"{nat_api}/memory/add"

            body = {
                "summary": "startup: duplicados detectados",
                "detail": msg,
                "channel": "startup",
                "project": "LLVC",
                "state": "vigente",
                "visibility": "equipo",
            }

            r = requests.post(mem_url, json=body, timeout=8)
            if r.status_code == 200:
                print("📝 startup: memoria creada por duplicados")
            else:
                print(f"⚠️ startup: no pude crear memoria ({r.status_code}): {r.text}")
        else:
            print("ℹ️ startup: no había duplicados que registrar")
    except Exception as e:
        print(f"⚠️ startup: fallo creando memoria de duplicados: {e}")


    # 4) memo de tareas sin fecha por proyecto
    try:
        if isinstance(data, dict) and "projects" in data:
            nat_api = os.getenv("NATACHA_CONTEXT_API") or api_base
            mem_url = f"{nat_api}/memory/add"
            for proj in data["projects"]:
                name = proj.get("name")
                alerts = proj.get("alerts") or []
                # buscamos alerta de tareas sin fecha
                no_due_alerts = [a for a in alerts if "sin fecha" in a.lower()]
                if no_due_alerts:
                    detail = f"Proyecto {name} tiene: " + ", ".join(no_due_alerts)
                    body = {
                        "summary": "startup: tareas sin fecha detectadas",
                        "detail": detail,
                        "channel": "startup",
                        "project": name or "LLVC",
                        "state": "vigente",
                        "visibility": "equipo",
                    }
                    import requests
                    r = requests.post(mem_url, json=body, timeout=8)
                    if r.status_code == 200:
                        print(f"📝 startup: memo de tareas sin fecha para {name}")
                    else:
                        print(f"⚠️ startup: no pude crear memo de tareas sin fecha ({r.status_code})")
    except Exception as e:
        print(f"⚠️ startup: fallo creando memo de tareas sin fecha: {e}")


    # 5) memo de tarea urgente detectada
    try:
        if isinstance(data, dict) and "projects" in data:
            nat_api = os.getenv("NATACHA_CONTEXT_API") or api_base
            mem_url = f"{nat_api}/memory/add"
            for proj in data["projects"]:
                name = proj.get("name")
                urgent = proj.get("urgent_task")
                if urgent:
                    title = urgent.get("title", "(sin título)")
                    due = urgent.get("due", "sin fecha")
                    detail = f"Tarea urgente en {name}: {title} (vence el {due})"
                    body = {
                        "summary": "startup: tarea urgente detectada",
                        "detail": detail,
                        "channel": "startup",
                        "project": name or "LLVC",
                        "state": "vigente",
                        "visibility": "equipo",
                    }
                    import requests
                    r = requests.post(mem_url, json=body, timeout=8)
                    if r.status_code == 200:
                        print(f"📝 startup: tarea urgente registrada para {name}")
                    else:
                        print(f"⚠️ startup: no pude registrar tarea urgente ({r.status_code})")
    except Exception as e:
        print(f"⚠️ startup: fallo creando memo de tarea urgente: {e}")

    print(f"✅ Contexto operativo cargado desde {used_url}")
    return data


if __name__ == "__main__":
    # permite correr:  python3 intelligence/startup.py
    api_base = os.getenv("NATACHA_CONTEXT_API") or "https://natacha-api-422255208682.us-central1.run.app"  # antiguo: https://natacha-api-mkwskljrhq-uc.a.run.app
    load_operational_context(api_base=api_base, limit=20)
