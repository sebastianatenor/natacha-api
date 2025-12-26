# ops/semantic/engine.py

import os
from typing import Optional
from sentence_transformers import SentenceTransformer

from ops.semantic.schema import SemanticAnalysis, SemanticSignal
from ops.semantic.state import SEMANTIC_STATE

# -------------------------------------------------
# Engine flags
# -------------------------------------------------

def semantic_enabled() -> bool:
    return os.getenv("SEMANTIC_ENGINE_ENABLED", "0") == "1"


# -------------------------------------------------
# Semantic Engine (heuristic + embeddings ready)
# -------------------------------------------------

class SemanticEngine:
    """
    Motor semántico PASIVO.
    - Detecta intención implícita
    - Puede usar heurística o embeddings
    - NO ejecuta
    """

    def __init__(self):
        self.model: Optional[SentenceTransformer] = None

    def _lazy_load(self):
        if self.model is not None:
            return

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        SEMANTIC_STATE.loaded = True
        SEMANTIC_STATE.model_name = "all-MiniLM-L6-v2"
        SEMANTIC_STATE.embedding_dim = (
            self.model.get_sentence_embedding_dimension()
        )

    def analyze(self, text: str) -> SemanticAnalysis:
        # Heurística básica (tu comportamiento original)
        t = text.lower()

        imperative_markers = [
            "hacelo", "hace", "hacé",
            "ejecuta", "ejecutá",
            "activa", "activá",
            "corre", "corré",
        ]

        automation_markers = [
            "automaticamente",
            "sin preguntar",
            "directamente",
            "ya mismo",
        ]

        implicit_action = (
            any(v in t for v in imperative_markers)
            and any(m in t for m in automation_markers)
        )

        if implicit_action:
            signals = SemanticSignal(
                intent="implicit_action",
                risk_level="high",
                domains=["automation"],
                confidence=0.9,
            )
        else:
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


# -------------------------------------------------
# Singleton + status (B16 requirement)
# -------------------------------------------------

_ENGINE: Optional[SemanticEngine] = None


def get_engine() -> Optional[SemanticEngine]:
    global _ENGINE

    if not semantic_enabled():
        return None

    if _ENGINE is None:
        _ENGINE = SemanticEngine()

    return _ENGINE


def semantic_status():
    return {
        "enabled": semantic_enabled(),
        "loaded": SEMANTIC_STATE.loaded,
        "model": SEMANTIC_STATE.model_name,
        "embedding_dim": SEMANTIC_STATE.embedding_dim,
        "mode": os.getenv("SEMANTIC_ENGINE_MODE", "heuristic"),
    }
