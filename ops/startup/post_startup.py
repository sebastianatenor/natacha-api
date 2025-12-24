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
# SEMANTIC CORE (CANONICAL)
# -----------------------------
if os.getenv("SEMANTIC_ENGINE_ENABLED") == "1":
    revision = os.getenv("K_REVISION")

    write_cognitive_state(
        subsystem="semantic",
        state="loading",
        revision=revision,
        confidence="medium"
    )

    try:
        from ops.semantic.runtime_loader import load_semantic_engine
        loaded = load_semantic_engine()

        write_cognitive_state(
            subsystem="semantic",
            state="loaded" if loaded else "error",
            revision=revision,
            confidence="high" if loaded else "medium",
            details={
                "source": "post_startup",
                "enabled": loaded
            }
        )

        print(f"[POST-STARTUP][SEMANTIC] Loaded = {loaded}")

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
            revision=revision,
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
    # COGNITIVE BOOT
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
    # DAILY SNAPSHOT
    # -----------------------------
    try:
        from ops.snapshots.daily_snapshot import write_daily_snapshot
        write_daily_snapshot()
        print("[POST-STARTUP][SNAPSHOT] Daily snapshot written")
    except Exception as e:
        print(f"[POST-STARTUP][SNAPSHOT][WARN] {e}")
