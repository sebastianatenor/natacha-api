# ops/semantic/engine.py

from typing import List
import re
import unicodedata

from sentence_transformers import SentenceTransformer

from ops.semantic.schema import SemanticAnalysis, SemanticSignal
from ops.semantic.state import SEMANTIC_STATE


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def normalize(text: str) -> str:
    """
    - lowercase
    - remove accents
    """
    text = text.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


# Raíces verbales (NO infinitivos)
IMPLICIT_ACTION_ROOTS = [
    "compr",
    "pag",
    "mand",
    "envi",
    "cre",
    "borr",
    "elimin",
    "ejecut",
    "activ",
    "desactiv",
    "automat",
]

AUTOMATION_MARKERS = [
    "automaticamente",
    "solo",
    "sin preguntar",
    "directamente",
    "ya mismo",
]


class SemanticEngine:
    """
    Motor semántico PASIVO.
    - Detecta intención implícita de acción
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
        t = normalize(text)

        verb_hit = any(root in t for root in IMPLICIT_ACTION_ROOTS)
        auto_hit = any(m in t for m in AUTOMATION_MARKERS)

        return verb_hit and auto_hit

    def analyze(self, text: str) -> SemanticAnalysis:
        implicit_action = self._detect_implicit_action(text)

        if implicit_action:
            signals = SemanticSignal(
                intent="implicit_action",
                risk_level="high",
                domains=["automation"],
                confidence=0.9,
            )

            return SemanticAnalysis(
                text=text,
                signals=signals,
                model_used="heuristic-v2",
            )

        # Fallback normal
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
            model_used="heuristic-v2",
        )


semantic_engine = SemanticEngine()
