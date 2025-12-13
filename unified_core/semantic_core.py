"""
Semantic Core – Cloud Run Safe (HF explicit token)
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

        # 🔑 token explícito (NO confiar en auto-detect)
        hf_token = os.getenv("HF_TOKEN")

        # 📦 cache forzado a /tmp (Cloud Run safe)
        os.environ.setdefault("HF_HOME", "/tmp/huggingface")
        os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/huggingface")

        if hf_token:
            self._model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                token=hf_token
            )
        else:
            raise RuntimeError("HF_TOKEN missing – cannot load semantic model")

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
