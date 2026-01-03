# ops/semantic/startup_guard.py
import os
from ops.cognitive.semantic_registry import register_semantic_event

def semantic_startup_guard():
    if not os.getenv("K_SERVICE"):
        register_semantic_event(
            state="unavailable",
            confidence="high",
            source="startup:no_cloud_run",
        )
        return

    if not os.getenv("HF_TOKEN"):
        register_semantic_event(
            state="unavailable",
            confidence="high",
            source="startup:no_hf_token",
        )
        return

    register_semantic_event(
        state="unloaded",
        confidence="high",
        source="startup:eligible",
    )
