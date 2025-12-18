# ops/startup/post_startup.py
import os
import threading
import time

from ops.cognitive.state_registry import write_cognitive_state


def post_startup_init():
    print("🔥 POST_STARTUP INIT")
    time.sleep(1)

    # -----------------------------
    # MEMORY
    # -----------------------------
    try:
        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")
    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    # -----------------------------
    # SEMANTIC CORE
    # -----------------------------
    if os.getenv("NATACHA_SEMANTIC_STARTUP") == "1":
        revision = os.getenv("K_REVISION")

        write_cognitive_state(
            subsystem="semantic",
            state="loading",
            revision=revision,
            confidence="medium"
        )

        try:
            from unified_core.semantic_core import get_semantic_core
            core = get_semantic_core()
            core.ensure_loaded()

            write_cognitive_state(
                subsystem="semantic",
                state="loaded",
                revision=revision,
                confidence="high",
                details={
                    "model": "sentence-transformers/all-MiniLM-L6-v2",
                    "cache": "/tmp/huggingface"
                }
            )

            print("[POST-STARTUP][SEMANTIC] Loaded & state committed")

        except Exception as e:
            write_cognitive_state(
                subsystem="semantic",
                state="error",
                revision=revision,
                confidence="medium",
                details={"error": str(e)}
            )
            print(f"[POST-STARTUP][SEMANTIC][ERROR] {e}")

    # -----------------------------
    # AUTO WARMUP
    # -----------------------------
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")

# -----------------------------
# REVISION CHECKPOINT (AUTOMÁTICO)
# -----------------------------
try:
    from ops.cognitive.state_registry import write_cognitive_state
    from datetime import datetime
    import os

    write_cognitive_state(
        subsystem="revision_checkpoint",
        state="written",
        revision=os.getenv("K_REVISION"),
        confidence="high",
        details={
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Automatic revision checkpoint"
        }
    )

    print("[POST-STARTUP][CHECKPOINT] Revision checkpoint written")

except Exception as e:
    print(f"[POST-STARTUP][CHECKPOINT][ERROR] {e}")

def launch_post_startup():
    threading.Thread(
        target=post_startup_init,
        daemon=True
    ).start()
