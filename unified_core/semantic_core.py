"""
Semantic Core – Cloud Run Hardened
- Lazy load
- HF token support
- In-memory embedding cache
"""

import os
import hashlib
from typing import Optional, List, Union, Dict
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None
        self._cache: Dict[str, List[float]] = {}

    def ensure_loaded(self):
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

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def embed(self, texts: Union[str, List[str]]):
        self.ensure_loaded()

        if isinstance(texts, str):
            texts = [texts]

        vectors = []
        missing = []
        missing_idx = []

        for i, t in enumerate(texts):
            h = self._hash(t)
            if h in self._cache:
                vectors.append(self._cache[h])
            else:
                vectors.append(None)
                missing.append(t)
                missing_idx.append(i)

        if missing:
            new_vecs = self._model.encode(missing)
            for i, vec in zip(missing_idx, new_vecs):
                h = self._hash(texts[i])
                self._cache[h] = vec.tolist()
                vectors[i] = self._cache[h]

        return vectors


# Singleton lazy
_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance
    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()
    return _semantic_core_instance
