"""
ops.cognitive_evolution
-----------------------
Módulo base del motor cognitivo evolutivo de Natacha.
Permite calcular métricas cognitivas y evaluar el estado evolutivo del sistema.
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path

router = APIRouter(prefix="/ops/cognitive", tags=["Cognitive Evolution"])

MEMORY_PATH = Path("/app/memory_store.jsonl")


def _load_latest_reflection() -> Dict[str, Any]:
    """Carga la última reflexión/meta-reflexión desde el archivo local."""
    if not MEMORY_PATH.exists():
        return {"status": "error", "message": "No se encontró memory_store.jsonl"}

    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-5:]
        reflections = [json.loads(line) for line in lines if "meta_reflection" in line or "reflection" in line]
        return reflections[-1] if reflections else {"status": "error", "message": "Sin reflexiones registradas"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/status")
def cognitive_status() -> Dict[str, Any]:
    """Devuelve el estado cognitivo actual."""
    latest = _load_latest_reflection()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "engine": "Cognitive Evolution v1",
        "latest_meta_reflection": latest.get("detail") if isinstance(latest, dict) else None,
        "status": "ok" if "error" not in latest.get("status", "") else "degraded"
    }


@router.post("/evolve")
def run_evolution() -> Dict[str, Any]:
    """Ejecuta un ciclo de evolución cognitiva basado en las introspecciones."""
    latest = _load_latest_reflection()

    score = 0.0
    trend = "unknown"

    if "detail" in latest:
        issues = len(latest["detail"].get("issues", []))
        score = max(0, 100 - issues * 5)
        trend = "improving" if score > 75 else "stable_or_worse"

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "cognitive_score": score,
        "trend": trend,
        "summary": "Autoevaluación cognitiva completada.",
        "source": "introspection/meta_reflection"
    }

    return {"status": "ok", "result": result}
