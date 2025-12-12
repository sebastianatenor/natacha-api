from sentence_transformers import SentenceTransformer
import threading

class SemanticCore:
    """
    SemanticCore con carga lazy para Cloud Run.
    El modelo se carga SOLO cuando se usa por primera vez.
    """

    _lock = threading.Lock()

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    print("[SEMANTIC] Loading SentenceTransformer model...")
                    self._model = SentenceTransformer("all-MiniLM-L6-v2")
                    print("[SEMANTIC] Model loaded")

    def embed(self, texts):
        self._load_model()
        return self._model.encode(texts)
