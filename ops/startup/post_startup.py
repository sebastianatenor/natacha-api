"""
ops.startup.post_startup
------------------------
Inicialización diferida (Cloud Run SAFE).
Todo lo pesado vive acá.
NO bloquea el arranque.
"""

import threading
import time
import os


print("🔥 POST_STARTUP FILE LOADED — SEMANTIC ENABLED VERSION")


def post_startup_init():
    """
    Se ejecuta luego de que Cloud Run ya dio READY.
    Todo lo que sea pesado va acá.
    """

    # --------------------------------------------------
    # Espera mínima para liberar event loop
    # --------------------------------------------------
    time.sleep(1)

    # --------------------------------------------------
    # MEMORIA (canónica, lazy)
    # --------------------------------------------------
    try:
        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")
    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    # --------------------------------------------------
    # SEMANTIC CORE (flagged)
    # --------------------------------------------------
    if os.getenv("NATACHA_SEMANTIC_STARTUP") == "1":
        try:
            from unified_core.semantic_core import get_semantic_core
            core = get_semantic_core()
            core.ensure_loaded()
            print("[POST-STARTUP] Semantic core loaded")
        except Exception as e:
            print(f"[POST-STARTUP][SEMANTIC][ERROR] {e}")
    else:
        print("[POST-STARTUP] Semantic startup skipped (flag off)")

    # --------------------------------------------------
    # AUTO WARMUP (opcional)
    # --------------------------------------------------
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")


def launch_post_startup():
    """
    Lanza la inicialización en background thread.
    """
    t = threading.Thread(
        target=post_startup_init,
        daemon=True
    )
    t.start()
