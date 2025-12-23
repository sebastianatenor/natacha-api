import threading
import time

def launch_semantic_warmup(max_retries: int = 3, delay: float = 2.0):
    """
    Warmup semántico:
    - Carga el modelo SentenceTransformer
    - NO escribe cognitive_state
    - NO depende de K_REVISION
    - Cloud Run safe
    """

    def _warmup():
        for attempt in range(1, max_retries + 1):
            try:
                from unified_core.semantic_core import get_semantic_core

                core = get_semantic_core()
                if core.is_loaded():
                    print("[WARMUP][SEMANTIC] already loaded")
                    return

                print(f"[WARMUP][SEMANTIC] loading model (attempt {attempt})")
                core.ensure_loaded()
                print("[WARMUP][SEMANTIC] loaded successfully")
                return

            except Exception as e:
                print(f"[WARMUP][SEMANTIC][WARN] attempt {attempt}: {e}")
                time.sleep(delay)

        print("[WARMUP][SEMANTIC][ERROR] failed after retries")

    t = threading.Thread(target=_warmup, daemon=True)
    t.start()
    print("[WARMUP] semantic warmup thread launched")
