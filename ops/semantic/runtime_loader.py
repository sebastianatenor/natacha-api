# ops/semantic/runtime_loader.py
import os
from typing import Optional

_semantic_engine = None


def load_semantic_engine() -> bool:
    """
    Loads semantic engine if enabled via env.
    Reports state to cognitive registry.
    """
    global _semantic_engine

    if os.getenv("SEMANTIC_ENGINE_ENABLED") != "1":
        return False

    try:
        from ops.semantic.engine import SemanticEngine
        from ops.cognitive.state_registry import write_cognitive_state

        revision = os.getenv("K_REVISION")

        engine = SemanticEngine()
        engine.load()

        _semantic_engine = engine

        write_cognitive_state(
            subsystem="semantic",
            state="loaded",
            revision=revision,
            confidence="high",
            details={
                "loader": "runtime_loader",
                "engine": engine.__class__.__name__,
            },
        )

        return True

    except Exception as e:
        from ops.cognitive.state_registry import write_cognitive_state

        write_cognitive_state(
            subsystem="semantic",
            state="error",
            revision=os.getenv("K_REVISION"),
            confidence="medium",
            details={"error": str(e)},
        )

        _semantic_engine = None
        return False


def get_semantic_engine():
    if _semantic_engine is None:
        raise RuntimeError("Semantic engine not loaded")
    return _semantic_engine
