"""
ops.introspection.meta_reflect
---------------------------------
Analiza reflexiones previas de Natacha ("self_reflection")
para detectar tendencias cognitivas: mejora, repetición o estancamiento.
"""

import json
from pathlib import Path
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/ops/introspection", tags=["Introspection"])


def load_reflections():
    """Carga todas las auto-reflexiones previas desde memory_store.jsonl."""
    path = Path("memory_store.jsonl")
    if not path.exists():
        return []
    reflections = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if '"self_reflection"' in line:
                try:
                    reflections.append(json.loads(line))
                except Exception:
                    continue
    return reflections


@router.get("/meta")
def meta_reflection():
    """
    Analiza las auto-reflexiones previas de Natacha
    y genera una evaluación de su evolución cognitiva.
    """
    reflections = load_reflections()
    if not reflections:
        return {
            "status": "error",
            "message": "No hay reflexiones previas almacenadas."
        }

    # Evaluar cantidad y tendencia
    count = len(reflections)
    first = reflections[0]["timestamp"]
    last = reflections[-1]["timestamp"]

    issues_trend = []
    for r in reflections:
        summary = r.get("summary", {})
        issues_trend.append(summary.get("issues_analyzed", 0))

    avg_issues = sum(issues_trend) / len(issues_trend) if issues_trend else 0
    trend = (
        "improving" if issues_trend[-1] < issues_trend[0]
        else "stable_or_worse"
    )

    # Generar reflexión cognitiva
    reflection_text = (
        "🧩 Meta-reflexión completada.\n\n"
        f"- Reflexiones totales: {count}\n"
        f"- Rango temporal: {first} → {last}\n"
        f"- Promedio de issues por análisis: {avg_issues:.2f}\n"
        f"- Tendencia general: {trend}\n\n"
    )

    if trend == "improving":
        reflection_text += "💡 La tendencia muestra una mejora constante en la calidad del código."
    else:
        reflection_text += "⚠️ Se detecta estancamiento o regresión. Reforzar documentación y limpieza estructural."

    return {
        "status": "ok",
        "reflections_analyzed": count,
        "trend": trend,
        "summary": {
            "avg_issues": avg_issues,
            "time_range": [first, last],
        },
        "meta_reflection": reflection_text,
    }
