"""
Semantic Core – Cloud Run Safe (HF explicit auth)
"""

import os
from typing import Optional, List, Union
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None

    def ensure_loaded(self):
        if self._model is not None:
            return

        print("[SEMANTIC] Loading SentenceTransformer model…")

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("HF_TOKEN missing")

        # Cloud Run writable cache
        os.environ.setdefault("HF_HOME", "/tmp/huggingface")
        os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/huggingface")

        self._model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            use_auth_token=hf_token   # 🔑 ESTA ES LA CLAVE
        )

        print("[SEMANTIC] Model loaded successfully")

    def embed(self, texts: Union[str, List[str]]):
        self.ensure_loaded()
        return self._model.encode(texts)


_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance
    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()
    return _semantic_core_instance
