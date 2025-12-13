"""
Semantic Core – Cloud Run Safe
Inicializa SentenceTransformer SOLO cuando se necesita.
Compatible con warmup explícito y HF token.
"""

import os
from typing import Optional, List, Union
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None

    def ensure_loaded(self):
        """
        Fuerza la carga del modelo si todavía no está cargado.
        Usa HF_TOKEN si está disponible.
        """
        if self._model is None:
            print("[SEMANTIC] Loading SentenceTransformer model…")

            hf_token = os.getenv("HF_TOKEN")

            if hf_token:
                self._model = SentenceTransformer(
                    "all-MiniLM-L6-v2",
                    use_auth_token=hf_token
                )
            else:
                self._model = SentenceTransformer("all-MiniLM-L6-v2")

            print("[SEMANTIC] Model loaded")

    def embed(self, texts: Union[str, List[str]]):
        self.ensure_loaded()
        return self._model.encode(texts)


# Singleton lazy
_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance
    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()
    return _semantic_core_instance
