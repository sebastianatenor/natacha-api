# ops/semantic/engine.py

from typing import List
import re

from sentence_transformers import SentenceTransformer

from ops.semantic.schema import SemanticAnalysis, SemanticSignal
from ops.semantic.state import SEMANTIC_STATE


IMPLICIT_ACTION_VERBS = [
    "comprar",
    "pagar",
    "crear",
    "eliminar",
    "borrar",
    "ejecutar",
    "mandar",
    "enviar",
    "activar",
    "desactivar",
    "automatizar",
    "hacer",
]

AUTOMATION_MARKERS = [
    "automáticamente",
    "solo",
    "sin preguntar",
    "directamente",
    "ya mismo",
]


class SemanticEngine:
    """
    Motor semántico PASIVO.
    - Detecta intención implícita
    - NO decide
    - NO ejecuta
    """

    def __init__(self):
        self.model = None

    def _lazy_load(self):
        if self.model is not None:
            return

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        SEMANTIC_STATE.loaded = True
        SEMANTIC_STATE.model_name = "all-MiniLM-L6-v2"
        SEMANTIC_STATE.embedding_dim = self.model.get_sentence_embedding_dimension()

    def _detect_implicit_action(self, text: str) -> bool:
        t = text.lower()

        verb_hit = any(re.search(rf"\b{v}\b", t) for v in IMPLICIT_ACTION_VERBS)
        auto_hit = any(m in t for m in AUTOMATION_MARKERS)

        return verb_hit and auto_hit

    def analyze(self, text: str) -> SemanticAnalysis:
        # Si no hay token HF, igual hacemos heurística
        implicit_action = self._detect_implicit_action(text)

        if implicit_action:
            signals = SemanticSignal(
                intent="implicit_action",
                risk_level="high",
                domains=["automation"],
                confidence=0.85,
            )

            return SemanticAnalysis(
                text=text,
                signals=signals,
                model_used="heuristic-v1",
            )

        # Si no hay acción implícita, seguimos flujo normal
        intent = "question" if "?" in text else "statement"

        signals = SemanticSignal(
            intent=intent,
            risk_level="low",
            domains=[],
            confidence=0.6,
        )

        return SemanticAnalysis(
            text=text,
            signals=signals,
            model_used="heuristic-v1",
        )


semantic_engine = SemanticEngine()

