from fastapi import APIRouter
from typing import Dict, Any
import time
import requests

router = APIRouter(
    prefix="/ops/system",
    tags=["system-decision"]
)


@router.get("/decide")
def system_decide() -> Dict[str, Any]:
    """
    Decisor automático PASIVO.
    Analiza el diagnóstico actual y sugiere acciones.
    NO ejecuta nada.
    """

    now = time.time()

    # Llamada interna al diagnóstico
    try:
        resp = requests.get("http://localhost:8080/ops/system/diagnose", timeout=2)
        diag = resp.json()
    except Exception as e:
        return {
            "timestamp": now,
            "status": "unknown",
            "error": f"cannot read diagnosis: {e}"
        }

    diagnosis = diag.get("diagnosis", {})
    warnings = diagnosis.get("warnings", [])
    summary = diagnosis.get("summary", {})

    recommendations = []

    if not summary.get("semantic_loaded"):
        recommendations.append({
            "action": "warmup_semantic_core",
            "endpoint": "/__warmup",
            "reason": "semantic core not loaded"
        })

    if not summary.get("memory_present"):
        recommendations.append({
            "action": "initialize_memory_store",
            "reason": "memory store not present on disk"
        })

    if not recommendations:
        status = "optimal"
    else:
        status = "actionable"

    return {
        "timestamp": now,
        "status": status,
        "recommendations": recommendations,
        "source": "passive_decision_engine"
    }
