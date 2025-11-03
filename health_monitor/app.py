import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Firestore (opcional, lo usamos en algunos endpoints)
from google.cloud import firestore

from app.debug_endpoints import router as debug_router
from health_monitor.auto_healer import auto_heal as auto_heal_fn

from .auto_scheduler import start_scheduler
from .cloud_services_scan import get_cloud_run_services

# Imports internos (sin fallbacks)
from .infra_local_history import clear_history, get_history, save_entry
from .infra_sync import pull_from_firestore, sync_local_to_firestore

app = FastAPI(title="Natacha Health Monitor")
app.include_router(debug_router)


def utc_now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")


# =====================================================
# 🩺 ENDPOINT PRINCIPAL
# =====================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "natacha-health-monitor activo"}


# =====================================================
# 🛠️ AUTO-HEALER POR HTTP (nuevo)
# =====================================================
@app.post("/auto_heal")
def trigger_auto_heal_fn():
    """
    Ejecuta escaneo + autocuración de servicios Cloud Run.
    Devuelve el resumen y lo registra en Firestore.
    """
    try:
        summary = auto_heal_fn()
        # Guarda un snapshot del resumen (con TS de servidor)
        try:
            db = firestore.Client()
            db.collection("auto_heal_runs").add(
                {**summary, "ts_server": firestore.SERVER_TIMESTAMP}
            )
        except Exception as e:
            print("⚠️ No se pudo guardar auto_heal_runs en Firestore:", str(e))
        return {"status": "ok", "data": summary}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "error", "detail": str(e)}
        )


# =====================================================
# 🚀 EJECUCIÓN DE DIAGNÓSTICO AUTOMÁTICO
# =====================================================
@app.post("/run_auto_infra_check")
def run_auto_infra_check():
    """
    Ejecuta un diagnóstico automático de infraestructura.
    Guarda el resultado tanto localmente como en Firestore (si está disponible).
    También incluye un escaneo real de servicios Cloud Run.
    """
    try:
        # 🔹 Recolectar servicios activos
        cloud_services = []
        try:
            cloud_services = get_cloud_run_services()
        except Exception as ce:
            print("⚠️ No se pudieron obtener servicios Cloud Run:", str(ce))

        result = {
            "timestamp": utc_now_str(),
            "environment": "cloudrun" if os.environ.get("K_SERVICE") else "local",
            "project": os.environ.get("GCP_PROJECT", "N/A"),
            "account": os.environ.get("GOOGLE_ACCOUNT", "N/A"),
            "vm_status": [],
            "docker_containers": [],
            "cloud_run_services": cloud_services,
            "disk_usage": "1%",
        }

        # 🔹 Guardar el diagnóstico localmente
        save_entry(result)

        # 🔹 Intentar guardar en Firestore
        try:
            save_to_firestore(result)
        except Exception as fe:
            print("⚠️ No se pudo guardar en Firestore:", str(fe))

        # 🔹 Intentar autocuración
        try:
            auto_heal_fn()
        except Exception as ae:
            print("⚠️ Error en auto-heal:", str(ae))

        return {
            "status": "ok",
            "detail": "Diagnóstico ejecutado correctamente",
            "data": result,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "error", "detail": str(e)}
        )


# =====================================================
# ☁️ GUARDADO EN FIRESTORE
# =====================================================
def save_to_firestore(data):
    """Guarda resultados del diagnóstico en Firestore (ADC/Workload Identity)."""
    try:
        db = firestore.Client()
        doc_ref = db.collection("infra_history").document(data["timestamp"])
        doc_ref.set(data)
        print(f"✅ Datos guardados en Firestore: {data['timestamp']}")
    except Exception as e:
        print(f"⚠️ Error al guardar en Firestore: {e}")


# =====================================================
# 📜 HISTORIAL LOCAL
# =====================================================
@app.get("/infra_history")
def infra_history():
    """Devuelve el historial local de diagnósticos."""
    try:
        data = get_history()
        return {"status": "ok", "count": len(data), "data": data}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.delete("/infra_clear")
def infra_clear():
    """Limpia el historial local de infraestructura."""
    try:
        clear_history()
        return {"status": "ok", "message": "Historial local eliminado correctamente"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# =====================================================
# 🔁 SINCRONIZACIÓN MANUAL CON FIRESTORE
# =====================================================
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


# =====================================================
# ⚙️ INICIO AUTOMÁTICO DE PROCESOS EN BACKGROUND
# =====================================================
@app.on_event("startup")
def startup_event():
    """Se ejecuta cuando el servicio inicia (ideal para Cloud Run o local)."""
    print("🚀 Iniciando Natacha Health Monitor...")
    try:
        start_scheduler()  # 🔁 Comienza el ciclo de diagnósticos automáticos
        print("✅ AutoScheduler iniciado correctamente.")
    except Exception as e:
        print("⚠️ No se pudo iniciar el AutoScheduler:", str(e))


# =====================================================
# 🧪 EJECUCIÓN LOCAL
# =====================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("health_monitor.app:app", host="0.0.0.0", port=8085, reload=True)
# --- std health endpoint (no side effects) ---
try:
    app  # ensure 'app' exists

    @app.get("/health", include_in_schema=False)
    def health():
        return {"status": "ok"}

except NameError:
    # If 'app' isn't available in this module, don't break imports
    pass
