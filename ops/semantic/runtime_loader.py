# ops/semantic/runtime_loader.py
import os

_semantic_loaded = False


def load_semantic_engine():
    global _semantic_loaded

    if os.getenv("SEMANTIC_ENGINE_ENABLED") != "1":
        return False

    try:
        from ops.semantic.engine import SemanticEngine
        engine = SemanticEngine()
        engine.load()
        _semantic_loaded = True
        return True
    except Exception:
        _semantic_loaded = False
        return False


def semantic_is_loaded() -> bool:
    return _semantic_loaded
