# ops/startup/post_startup.py
import os
import threading
import time
from datetime import datetime

from ops.cognitive.state_registry import write_cognitive_state


def _post_startup_worker():
    print("🔥 POST_STARTUP WORKER STARTED")
    time.sleep(2)

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
        return

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

            print("[POST-STARTUP][SEMANTIC] Loaded")

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
    # REVISION CHECKPOINT
    # -----------------------------
    try:
        write_cognitive_state(
            subsystem="revision_checkpoint",
            state="written",
            revision=os.getenv("K_REVISION"),
            confidence="high",
            details={
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Post-startup canonical checkpoint"
            }
        )
        print("[POST-STARTUP][CHECKPOINT] Revision checkpoint written")
    except Exception as e:
        print(f"[POST-STARTUP][CHECKPOINT][ERROR] {e}")

    # -----------------------------
    # COGNITIVE BOOT (B3)
    # -----------------------------
    try:
        from ops.system.perception_provider import get_system_perception
        from ops.cognitive.boot_writer import write_cognitive_boot

        perception = get_system_perception()
        write_cognitive_boot(perception)

        print("[POST-STARTUP][BOOT] Cognitive boot persisted")

    except Exception as e:
        print(f"[POST-STARTUP][BOOT][WARN] {e}")


def launch_post_startup():
    threading.Thread(
        target=_post_startup_worker,
        daemon=True
    ).start()

    # -----------------------------
    # DAILY SNAPSHOT (REAL STATE)
    # -----------------------------
    try:
        from ops.snapshots.daily_snapshot import write_daily_snapshot
        write_daily_snapshot()
        print("[POST-STARTUP][SNAPSHOT] Daily snapshot written")
    except Exception as e:
        print(f"[POST-STARTUP][SNAPSHOT][WARN] {e}")
