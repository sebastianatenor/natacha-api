"""
🤖 context_reasoner.py
Módulo de razonamiento contextual del Core.
Integra memoria reciente y análisis semántico simple para respuestas más coherentes.
"""

import datetime
from typing import List, Dict

def summarize_context(context_items: List[Dict]) -> str:
    """Genera un resumen textual simple del contexto reciente."""
    if not context_items:
        return "No hay contexto previo registrado."
    texts = [item.get("text", "") for item in context_items[:3]]
    return " | ".join(texts)

def generate_response(user_text: str, context_items: List[Dict]) -> Dict:
    """Produce una respuesta razonada basada en el texto y el contexto reciente."""
    context_summary = summarize_context(context_items)
    reasoning = "Entiendo que estás retomando una conversación previa." if context_items else "Parece que es la primera vez que hablamos."

    return {
        "timestamp": str(datetime.datetime.utcnow()),
        "user_text": user_text,
        "context_summary": context_summary,
        "reasoning": reasoning,
        "response": f"{reasoning} Me dijiste: '{user_text}'. Contexto: {context_summary}"
    }
