"""
Semantic Core – Cloud Run SAFE (HF env-based auth)
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

        # 🔑 NORMALIZAR TOKEN (CRÍTICO EN CLOUD RUN)
        hf_token = hf_token.strip()

        # 👉 HuggingFace HUB espera ESTE nombre
        os.environ["HUGGINGFACE_HUB_TOKEN"] = hf_token

        # Cache writable (Cloud Run safe)
        os.environ.setdefault("HF_HOME", "/tmp/huggingface")
        os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/huggingface")

        # 🚫 NO pasar token como argumento
        self._model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        self._loaded = True
        print("[SEMANTIC] Model loaded successfully")

    def is_loaded(self) -> bool:
        return self._loaded

    def embed(self, text: str) -> List[float]:
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
