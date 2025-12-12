"""
Semantic Core – Cloud Run Safe
Inicializa SentenceTransformer SOLO cuando se usa.
"""

from typing import Optional
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self):
        if self._model is None:
            print("[SEMANTIC] Loading SentenceTransformer model…")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[SEMANTIC] Model loaded")

    def embed(self, texts):
        self._load_model()
        return self._model.encode(texts)


# 🔑 Singleton LAZY (NO se instancia al importar)
_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance

    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()

    return _semantic_core_instance
