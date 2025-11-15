"""
📈 adaptive_trainer.py
Sistema de aprendizaje adaptativo básico que acumula estadísticas
de claridad y coherencia del Core Cognitivo.
"""

import datetime

# Estado adaptativo global
_metrics = {
    "evaluations": 0,
    "avg_clarity": 0.0,
    "avg_coherence": 0.0,
    "last_update": None,
}

def update_metrics(evaluation):
    """Actualiza las métricas globales del sistema adaptativo."""
    global _metrics

    clarity = evaluation.get("clarity_score", 0.0)
    coherence = evaluation.get("coherence_score", 0.0)
    n = _metrics["evaluations"]

    _metrics["evaluations"] = n + 1
    _metrics["avg_clarity"] = (_metrics["avg_clarity"] * n + clarity) / (n + 1)
    _metrics["avg_coherence"] = (_metrics["avg_coherence"] * n + coherence) / (n + 1)
    _metrics["last_update"] = datetime.datetime.utcnow().isoformat()

    return {"status": "ok", "stats": _metrics}

def get_stats():
    """Devuelve las métricas acumuladas del sistema adaptativo."""
    return {"status": "ok", "stats": _metrics}
