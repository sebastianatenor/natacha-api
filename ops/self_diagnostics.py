"""
ops.self_diagnostics
---------------------
Sistema de diagnóstico interno de Natacha.
Verifica integridad funcional y consistencia de componentes.
"""

from fastapi import APIRouter
from datetime import datetime
from pathlib import Path
import subprocess

router = APIRouter(prefix="/ops/self", tags=["Self Diagnostics"])

CHECK_PATHS = [
    "/app/memory_store.jsonl",
    "/app/ops/introspection/meta_reflect.py",
]


def _check_file_exists(path: str) -> bool:
    return Path(path).exists()


def _check_gcloud() -> bool:
    """Verifica si el CLI de Google Cloud está disponible en el contenedor."""
    try:
        subprocess.run(["gcloud", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False


@router.get("/diagnostics")
def run_diagnostics():
    """Ejecuta diagnóstico del sistema."""
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "memory_store": _check_file_exists(CHECK_PATHS[0]),
            "introspection_core": _check_file_exists(CHECK_PATHS[1]),
        },
        "gcloud_available": _check_gcloud(),
        "status": "ok"
    }

    if not all(results["checks"].values()):
        results["status"] = "degraded"

    return results
