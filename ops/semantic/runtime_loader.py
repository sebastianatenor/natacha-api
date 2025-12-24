# ops/semantic/runtime_loader.py
import os

_semantic_loaded = False
_semantic_engine = None


def load_semantic_engine() -> bool:
    """
    Loads semantic engine if enabled via env.
    This is the SINGLE source of truth for semantic state.
    """
    global _semantic_loaded, _semantic_engine

    if os.getenv("SEMANTIC_ENGINE_ENABLED") != "1":
        _semantic_loaded = False
        return False

    try:
        from ops.semantic.engine import SemanticEngine

        engine = SemanticEngine()
        engine.load()

        _semantic_engine = engine
        _semantic_loaded = True
        return True

    except Exception as e:
        print(f"[SEMANTIC][ERROR] load failed: {e}")
        _semantic_loaded = False
        _semantic_engine = None
        return False


def semantic_is_loaded() -> bool:
    return _semantic_loaded


def get_semantic_engine():
    if not _semantic_loaded:
        raise RuntimeError("Semantic engine not loaded")
    return _semantic_engine
