import datetime
import json
from collections import deque
from adaptive_store import save_state, load_state

# Últimas 5 evaluaciones (ventana móvil)
_recent_window = deque(maxlen=5)

# Métricas acumuladas globales
_metrics = {
"""
📊 adaptive_trainer.py
Sistema de aprendizaje adaptativo de Natacha con persistencia local.
"""

import datetime
from adaptive_store import save_state, load_state

# Cargar métricas previas desde disco
_state = load_state()

_metrics = _state if isinstance(_state, dict) and "evaluations" in _state else {
    "evaluations": 0,
    "avg_clarity": 0.0,
    "avg_coherence": 0.0,
    "last_update": None,
}

def update_metrics(evaluation: dict):
    """Actualiza métricas adaptativas con ventana móvil."""
    clarity = evaluation.get("clarity_score", 0)
    coherence = evaluation.get("coherence_score", 0)

    # Guardar evaluación en ventana móvil
    _recent_window.append({"clarity": clarity, "coherence": coherence})

    # Calcular promedios móviles
    if _recent_window:
        clarity_avg = sum(i["clarity"] for i in _recent_window) / len(_recent_window)
        coherence_avg = sum(i["coherence"] for i in _recent_window) / len(_recent_window)
    else:
        clarity_avg = coherence_avg = 0

    # Actualizar métricas globales
    _metrics["evaluations"] += 1
    _metrics["avg_clarity"] = round(clarity_avg, 3)
    _metrics["avg_coherence"] = round(coherence_avg, 3)
    _metrics["last_update"] = datetime.datetime.utcnow().isoformat()

    # Guardar estado persistente y sincronizar con GCS
def update_metrics(eval_result):
    """Actualiza las métricas adaptativas acumuladas y las guarda en disco."""
    clarity = eval_result.get("clarity_score", 0.0)
    coherence = eval_result.get("coherence_score", 0.0)

    n = _metrics["evaluations"]
    _metrics["evaluations"] = n + 1
    _metrics["avg_clarity"] = (_metrics["avg_clarity"] * n + clarity) / (n + 1)
    _metrics["avg_coherence"] = (_metrics["avg_coherence"] * n + coherence) / (n + 1)
    _metrics["last_update"] = datetime.datetime.utcnow().isoformat()

    # Guardar en disco
    save_state(_metrics)

    return {"status": "ok", "stats": _metrics}


def get_stats():
    """Devuelve métricas acumuladas (globales + ventana móvil)."""
    saved = load_state() or {}
    return {
        "status": "ok",
        "stats": {
            **_metrics,
            "window_size": len(_recent_window),
            "window_clarity": [r["clarity"] for r in _recent_window],
            "window_coherence": [r["coherence"] for r in _recent_window],
            "persisted_avg_clarity": saved.get("avg_clarity"),
            "persisted_avg_coherence": saved.get("avg_coherence"),
        },
    }
def get_stats():
    """Devuelve las métricas acumuladas del sistema adaptativo."""
    return {"status": "ok", "stats": _metrics}
