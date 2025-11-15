"""
🧠 cognitive_evaluator.py
Módulo de evaluación cognitiva: analiza la coherencia y claridad del contexto.
"""

import math
import statistics
from typing import List, Dict

def evaluate_context_quality(context_items: List[Dict]) -> Dict:
    """Evalúa la calidad cognitiva del contexto reciente."""
    if not context_items:
        return {
            "context_items": 0,
            "clarity_score": 0.0,
            "coherence_score": 0.0,
            "status": "no_context"
        }

    lengths = [len(item.get("text", "")) for item in context_items if item.get("text")]
    avg_len = statistics.mean(lengths) if lengths else 0
    stdev = statistics.stdev(lengths) if len(lengths) > 1 else 0

    # Claridad = cuanto más uniformes los mensajes, mayor claridad
    clarity = max(0, 1 - (stdev / (avg_len + 1e-6)))
    # Coherencia = función logarítmica de la cantidad y tamaño medio
    coherence = math.tanh(len(context_items) * avg_len / 100.0)

    return {
        "context_items": len(context_items),
        "clarity_score": round(clarity, 3),
        "coherence_score": round(coherence, 3),
        "status": "ok"
    }
