# ops/startup/post_startup.py
import threading
import time
import os

def post_startup_init():
    """
    Todo lo pesado va acá.
    Cloud Run ya dio READY cuando esto corre.
    """

    # --------------------------------------------------
    # 1) MEMORIA (ya existente)
    # --------------------------------------------------
    try:
        print("[POST-STARTUP] Starting delayed init...")
        time.sleep(1)

        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")

    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    # --------------------------------------------------
    # 2) AUTO-WARMUP (ya existente)
    # --------------------------------------------------
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")

    # --------------------------------------------------
    # 3) SEMANTIC CORE (NUEVO – PASIVO, SAFE)
    # --------------------------------------------------
    try:
        if not os.getenv("HF_TOKEN"):
            print("[POST-STARTUP][SEMANTIC] HF_TOKEN not present → skipping")
            return

        print("[POST-STARTUP][SEMANTIC] HF_TOKEN detected")

        from unified_core.semantic_core import get_semantic_core
        core = get_semantic_core()

        if core.is_loaded():
            print("[POST-STARTUP][SEMANTIC] Semantic core already loaded")
            return

        print("[POST-STARTUP][SEMANTIC] Initializing semantic core (background)")
        core.ensure_loaded()
        print("[POST-STARTUP][SEMANTIC] Semantic core loaded ✅")

    except Exception as e:
        print(f"[POST-STARTUP][SEMANTIC][ERROR] {e}")


def launch_post_startup():
    """
    Se lanza SIEMPRE en background.
    Nunca bloquea arranque.
    """
    t = threading.Thread(
        target=post_startup_init,
        daemon=True
    )
    t.start()
