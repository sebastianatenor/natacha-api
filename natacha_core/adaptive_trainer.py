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
    """Devuelve las métricas acumuladas del sistema adaptativo."""
    return {"status": "ok", "stats": _metrics}
