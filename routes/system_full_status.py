# routes/system_full_status.py
from fastapi import APIRouter
from datetime import datetime
import os
import time

from ops.memory.canonical_state import memory_state
from ops.memory.manager import user_context_manager
from ops.system.capability_reader import read_capability_manifest

router = APIRouter(tags=["system"])


@router.get("/ops/system/full_status")
def system_full_status(
    user_id: str | None = None,
    include_semantic: bool = True,
):
    """
    Estado global del sistema con fuente de verdad unificada.

    PRIORIDAD DE VERDAD:
    1. capability_manifest (estado sellado del sistema)
    2. runtime perception (estado real)
    3. memoria histórica / introspectiva
    """

    now_ts = time.time()

    # =========================
    # 🔐 Capability Manifest (SOURCE OF TRUTH)
    # =========================
    capability_manifest = read_capability_manifest()

    # =========================
    # Runtime
    # =========================
    runtime = {
        "cloud_run": os.getenv("K_SERVICE") is not None,
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "python": os.getenv("PYTHON_VERSION", "3.10.x"),
    }

    # =========================
    # Infra
    # =========================
    infra = {
        "health_routes": "loaded",
    }

    # =========================
    # Semantic (CANONICAL — timeline)
    # =========================
    semantic_loaded = False
    semantic_source = "unknown"

    try:
        from ops.timeline.reader import read_events
        events = read_events()

        for ev in reversed(events):
            if ev.get("subsystem") == "semantic":
                semantic_loaded = ev.get("state") == "loaded"
                semantic_source = "timeline"
                break
    except Exception:
        semantic_loaded = False
        semantic_source = "error"

    semantic = {
        "loaded": semantic_loaded,
        "hf_token_present": bool(os.getenv("HF_TOKEN")),
        "mode": "canonical",
        "source": semantic_source,
    }

    # =========================
    # Memory (CANONICAL)
    # =========================
    memory = memory_state()

    # =========================
    # Context / Introspection
    # =========================
    context = {
        "unified": "loaded",
    }

    introspection = {
        "history": "loaded",
        "meta": "loaded",
    }

    # =========================
    # Base status (A)
    # =========================
    status = {
        "timestamp": now_ts,
        "generated_at": datetime.utcnow().isoformat(),
        "mode": "A",
        "source_of_truth": "capability_manifest > runtime > historical_memory",
        "capability_manifest": capability_manifest,
        "runtime": runtime,
        "infra": infra,
        "semantic": semantic,
        "memory": memory,
        "context": context,
        "introspection": introspection,
    }

    # =========================
    # User live cognitive state (READ ONLY)
    # =========================
    if user_id:
        try:
            status["user_state"] = user_context_manager.snapshot(user_id)
        except Exception:
            status["user_state"] = "unavailable"

    # =========================
    # 🅱️ MODO B (EXTENDIDO – NO AUTORITATIVO)
    # =========================
    if os.getenv("NATACHA_SELF_EXTENDED") == "1":
        status["mode"] = "A+B"
        extended = {}

        # Introspección histórica (informativa, no declarativa)
        try:
            from ops.introspection.history_reader import read_history
            extended["introspection_history"] = read_history(limit=5)
        except Exception:
            extended["introspection_history"] = "not_loaded"

        # Evolución cognitiva (informativa)
        try:
            from ops.cognitive_evolution import cognitive_status
            extended["cognitive_evolution"] = cognitive_status()
        except Exception:
            extended["cognitive_evolution"] = "not_loaded"

        extended["note"] = (
            "Extended mode is informational only. "
            "Capability manifest remains the authoritative source."
        )

        status["extended"] = extended

    return status
