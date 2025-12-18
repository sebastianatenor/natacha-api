"""
Semantic Core – Cloud Run Safe (HF explicit auth)
"""

import os
from typing import Optional, List
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None
        self._loaded: bool = False

    def ensure_loaded(self):
        if self._loaded:
            return

        print("[SEMANTIC] Loading SentenceTransformer model…")

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("HF_TOKEN missing")

        # 🔧 FIX CRÍTICO: limpiar whitespace / newline del secret
        hf_token = hf_token.strip()

        # Cloud Run writable cache
        os.environ.setdefault("HF_HOME", "/tmp/huggingface")
        os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/huggingface")

        self._model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            use_auth_token=hf_token
        )

        self._loaded = True
        print("[SEMANTIC] Model loaded successfully")

    def is_loaded(self) -> bool:
        return self._loaded

    def embed(self, text: str) -> List[float]:
        """
        Devuelve embedding vectorial del texto.
        Safe para lazy-load y Cloud Run.
        """
        self.ensure_loaded()

        if self._model is None:
            raise RuntimeError("Semantic model not loaded")

        vec = self._model.encode(text)
        return vec.tolist()


_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance
    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()
    return _semantic_core_instance
