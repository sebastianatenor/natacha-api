"""
Semantic Core — Lazy, Cloud Run safe, deterministic
"""

import os
from typing import Optional, List
from sentence_transformers import SentenceTransformer


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None
        self._loaded: bool = False
        self._loading: bool = False

    def ensure_loaded(self):
        if self._loaded:
            return

        if self._loading:
            raise RuntimeError("Semantic model is currently loading")

        self._loading = True
        try:
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                raise RuntimeError("HF_TOKEN missing")

            # Cloud Run writable cache
            os.environ.setdefault("HF_HOME", "/tmp/huggingface")
            os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
            os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/huggingface")

            print("[SEMANTIC] Lazy loading SentenceTransformer model…")

            self._model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                use_auth_token=hf_token.strip()
            )

            self._loaded = True
            print("[SEMANTIC] Model loaded successfully")

        finally:
            self._loading = False

    def is_loaded(self) -> bool:
        return self._loaded

    def embed(self, text: str) -> List[float]:
        if not text:
            raise ValueError("Text is empty")

        self.ensure_loaded()

        if not self._model:
            raise RuntimeError("Semantic model unavailable")

        vec = self._model.encode(text)
        return vec.tolist()


_semantic_core_instance: Optional[SemanticCore] = None


def get_semantic_core() -> SemanticCore:
    global _semantic_core_instance
    if _semantic_core_instance is None:
        _semantic_core_instance = SemanticCore()
    return _semantic_core_instance

# =====================================================
# FAISS PERSISTENCE (CANONICAL)
# =====================================================
def persist_faiss_index(index):
    try:
        import faiss
        from google.cloud import storage
        from unified_core.vector_paths import (
            VECTOR_INDEX_LOCAL,
            GCS_BUCKET,
            VECTOR_INDEX_BLOB,
        )

        # Save locally (Cloud Run safe)
        faiss.write_index(index, str(VECTOR_INDEX_LOCAL))

        # Upload to GCS
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(VECTOR_INDEX_BLOB)
        blob.upload_from_filename(str(VECTOR_INDEX_LOCAL))

        print("[VECTOR] FAISS index persisted to GCS")

    except Exception as e:
        print(f"[VECTOR][WARN] FAISS persist failed: {e}")
