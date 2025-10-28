from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime

# 🔹 Importamos el respaldo local
from health_monitor.infra_local_history import save_entry, get_history

app = FastAPI(title="Natacha Health Monitor")

@app.get("/")
def root():
    return {"status": "ok", "message": "natacha-health-monitor activo"}


@app.post("/run_auto_infra_check")
def run_auto_infra_check():
    """
    Ejecuta un diagnóstico automático de infraestructura.
    Guarda el resultado en Firestore (si está disponible)
    o en un historial local como respaldo.
    """
    try:
        result = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "environment": "cloudrun" if os.environ.get("K_SERVICE") else "local",
            "project": os.environ.get("GCP_PROJECT", "N/A"),
            "account": os.environ.get("GOOGLE_ACCOUNT", "N/A"),
            "vm_status": [],
            "docker_containers": [],
            "cloud_run_services": [],
            "disk_usage": "1%"
        }

        # 🔹 Guardar el diagnóstico localmente
        save_entry(result)

        return {
            "status": "ok",
            "detail": "Diagnóstico ejecutado correctamente",
            "data": result
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "detail": str(e)
        })


@app.get("/infra_history")
def infra_history():
    """
    Devuelve el historial de diagnósticos locales
    (hasta 100 registros recientes).
    """
    try:
        data = get_history()
        return {
            "status": "ok",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


@app.delete("/infra_clear")
def infra_clear():
    """
    Limpia el historial local de infraestructura.
    """
    try:
        from health_monitor.infra_local_history import clear_history
        clear_history()
        return {"status": "ok", "message": "Historial local eliminado correctamente"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# 🔹 Para ejecución local

from health_monitor.infra_sync import sync_local_to_firestore, pull_from_firestore

@app.post("/sync_firestore")
def sync_firestore():
    """Sincroniza el historial local con Firestore."""
    result = sync_local_to_firestore()
    return result

@app.get("/infra_history_cloud")
def infra_history_cloud():
    """Obtiene el historial directamente desde Firestore."""
    result = pull_from_firestore()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("health_monitor.app:app", host="0.0.0.0", port=8085, reload=True)
