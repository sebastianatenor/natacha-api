# ops/startup/post_startup.py
import threading
import time
import os

def post_startup_init():
    """
    Todo lo pesado va acá.
    Cloud Run ya dio READY cuando esto corre.
    """
    try:
        print("[POST-STARTUP] Starting delayed init...")
        time.sleep(1)

        # ---------------------------
        # Memory (ya existente)
        # ---------------------------
        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")

    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    # ---------------------------
    # Semantic Core (NUEVO, PERO CAMINO EXISTENTE)
    # ---------------------------
    if os.getenv("NATACHA_SEMANTIC_STARTUP") == "1":
        try:
            from unified_core.semantic_core import get_semantic_core
            core = get_semantic_core()
            core.ensure_loaded()
            print("[POST-STARTUP] Semantic core loaded")
        except Exception as e:
            print(f"[POST-STARTUP][SEMANTIC][ERROR] {e}")

    # ---------------------------
    # Auto warmup (ya existente)
    # ---------------------------
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")


def launch_post_startup():
    t = threading.Thread(
        target=post_startup_init,
        daemon=True
    )
    t.start()
