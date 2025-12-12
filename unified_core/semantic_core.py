"""
Semantic Core – Cloud Run Safe
Inicializa SentenceTransformer SOLO cuando se necesita.
Compatible con warmup explícito.
"""

from typing import Optional, List, Union
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None

    # ==========================================================
    # Carga controlada (NO en import, NO en init)
    # ==========================================================
    def ensure_loaded(self):
        """
        Fuerza la carga del modelo si todavía no está cargado.
        Seguro para Cloud Run y warmup explícito.
        """
        if self._model is None:
            print("[SEMANTIC] Loading SentenceTransformer model…")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[SEMANTIC] Model loaded")

    # ==========================================================
    # API principal de embeddings
    # ==========================================================
    def embed(self, texts: Union[str, List[str]]):
        """
        Genera embeddings asegurando que el modelo esté cargado.
        """
        self.ensure_loaded()
        return self._model.encode(texts)


# ==========================================================
# Singleton LAZY (NO se instancia al importar)
# ==========================================================

_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance

    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()

    return _semantic_core_instance
