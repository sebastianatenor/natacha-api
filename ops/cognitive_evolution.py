"""
ops.cognitive_evolution
-----------------------
Motor cognitivo evolutivo para Natacha.
Genera reflexiones, lee introspecciones y produce un estado cognitivo real.
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path

router = APIRouter(prefix="/ops/cognitive", tags=["Cognitive Evolution"])

# Memoria cognitiva local
MEMORY_PATH = Path("./memory_store.jsonl")


def _load_latest_reflection() -> Dict[str, Any]:
    """Devuelve la última reflexión/meta-reflexión registrada."""
    if not MEMORY_PATH.exists():
        return {"status": "error", "message": "memory_store.jsonl no encontrado"}

    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        reflections = []
        for line in lines:
            try:
                obj = json.loads(line)
                if "reflection" in obj or "meta_reflection" in obj:
                    reflections.append(obj)
            except:
                continue

        return reflections[-1] if reflections else {"status": "no_reflections"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _append_reflection(data: Dict[str, Any]):
    """Guarda una reflexión en el archivo de memoria."""
    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


@router.post("/reflect")
def write_reflection(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agrega una reflexión cognitiva manual o automática.
    """
    reflection = {
        "timestamp": datetime.utcnow().isoformat(),
        "reflection": payload,
    }
    _append_reflection(reflection)
    return {"status": "ok", "saved": reflection}


@router.post("/meta")
def write_meta_reflection(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agrega una meta-reflexión (evaluación del sistema sobre sí mismo).
    """
    meta = {
        "timestamp": datetime.utcnow().isoformat(),
        "meta_reflection": payload,
    }
    _append_reflection(meta)
    return {"status": "ok", "saved": meta}


@router.get("/status")
def cognitive_status() -> Dict[str, Any]:
    """Devuelve estado cognitivo basado en la última meta-reflexión."""
    latest = _load_latest_reflection()

    if "meta_reflection" not in latest:
        return {
            "status": "no_data",
            "engine": "Cognitive Evolution v2",
            "message": "No hay meta-reflexiones aún"
        }

    issues = len(latest["meta_reflection"].get("issues", []))
    score = max(0, 100 - issues * 4)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "engine": "Cognitive Evolution v2",
        "score": score,
        "trend": "improving" if score > 75 else "needs_attention",
        "latest": latest["meta_reflection"],
        "status": "ok"
    }
