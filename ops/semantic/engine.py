from typing import List
from sentence_transformers import SentenceTransformer

from ops.semantic.schema import SemanticAnalysis, SemanticSignal
from ops.semantic.state import SEMANTIC_STATE


class SemanticEngine:
    """
    Motor semántico REAL (embeddings).
    - No decide
    - No ejecuta
    - Solo clasifica significado
    """

    def __init__(self):
        self.model = None

    def _lazy_load(self):
        if self.model is not None:
            return

        # Modelo chico, rápido y estable
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        SEMANTIC_STATE.loaded = True
        SEMANTIC_STATE.model_name = "all-MiniLM-L6-v2"
        SEMANTIC_STATE.embedding_dim = self.model.get_sentence_embedding_dimension()

    def analyze(self, text: str) -> SemanticAnalysis:
        if not SEMANTIC_STATE.hf_token_present:
            return SemanticAnalysis(
                text=text,
                signals=SemanticSignal(
                    intent="unknown",
                    risk_level="unknown",
                    domains=[],
                    confidence=0.0,
                ),
                model_used=None,
            )

        self._lazy_load()

        embedding = self.model.encode(text)

        # Heurística mínima (placeholder consciente)
        intent = "question" if "?" in text else "statement"

        signals = SemanticSignal(
            intent=intent,
            risk_level="low",
            domains=[],
            confidence=0.65,
        )

        return SemanticAnalysis(
            text=text,
            signals=signals,
            model_used=SEMANTIC_STATE.model_name,
            embedding_dim=len(embedding),
        )


semantic_engine = SemanticEngine()
