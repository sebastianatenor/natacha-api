import os
import threading

def _warmup_async():
    try:
        from unified_core.semantic_core import get_semantic_core
        core = get_semantic_core()
        core.ensure_loaded()
        print("[AUTO-WARMUP] Semantic core loaded")
    except Exception as e:
        print(f"[AUTO-WARMUP][ERROR] {e}")

def maybe_auto_warmup():
    """
    Ejecuta warmup interno SOLO si:
    - Estamos en Cloud Run
    - NATACHA_AUTO_WARMUP=true
    """
    if os.getenv("K_SERVICE") and os.getenv("NATACHA_AUTO_WARMUP", "false") == "true":
        t = threading.Thread(target=_warmup_async, daemon=True)
        t.start()
        print("[AUTO-WARMUP] Triggered")
