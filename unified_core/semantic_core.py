"""
Semantic Core – Cloud Run Safe (HF Token Compatible)
Carga SentenceTransformer de forma lazy y segura.
"""

import os
from typing import Optional, List, Union
from sentence_transformers import SentenceTransformer
import os

os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from huggingface_hub import login


class SemanticCore:
    def __init__(self):
        self._model: Optional[SentenceTransformer] = None

    def ensure_loaded(self):
        if self._model is not None:
            return

        print("[SEMANTIC] Loading SentenceTransformer model…")

        hf_token = os.getenv("HF_TOKEN")

        if hf_token:
            # ✅ Forma CORRECTA actual
            login(token=hf_token, add_to_git_credential=False)
            print("[SEMANTIC] HuggingFace token loaded")

        # 🔥 Descarga autenticada si hay token
        self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        print("[SEMANTIC] Model loaded successfully")

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
