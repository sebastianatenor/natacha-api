import threading
import time

def post_startup_init():
    """
    Todo lo pesado va acá.
    Cloud Run ya dio READY cuando esto corre.
    """
    try:
        print("[POST-STARTUP] Starting delayed init...")

        # pequeña espera para liberar event loop
        time.sleep(1)

        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")

    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")

    # --------------------------------------------------
    # Symbolic reasoning (Mode F) – gated
    # --------------------------------------------------
    try:
        if os.getenv("NATACHA_SYMBOLIC_STARTUP") == "1":
            from ops.cognitive.symbolic_rules import run_symbolic_rules
            from pathlib import Path
            import json

            MEMORY_PATH = Path("memory_store.jsonl")
            inferences = run_symbolic_rules()

            if inferences:
                with MEMORY_PATH.open("a", encoding="utf-8") as f:
                    for inf in inferences:
                        f.write(json.dumps(inf, ensure_ascii=False) + "\n")

                print(f"[POST-STARTUP] Symbolic inferences persisted: {len(inferences)}")
            else:
                print("[POST-STARTUP] No symbolic inferences (stable state)")
    except Exception as e:
        print(f"[POST-STARTUP][SYMBOLIC][ERROR] {e}")

def launch_post_startup():
    t = threading.Thread(
        target=post_startup_init,
        daemon=True
    )
    t.start()
