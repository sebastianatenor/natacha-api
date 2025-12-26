# ops/semantic/loader.py
from ops.semantic.engine import semantic_engine
from ops.semantic.state import SEMANTIC_STATE
from ops.timeline.writer import write_event


def init_semantic_engine(force: bool = False) -> dict:
    """
    Explicit semantic engine initialization.
    - Lazy load
    - No auto side-effects
    - Timeline is source of truth
    """

    if SEMANTIC_STATE.loaded and not force:
        return {
            "status": "noop",
            "reason": "already_loaded",
            "model": SEMANTIC_STATE.model_name,
            "embedding_dim": SEMANTIC_STATE.embedding_dim,
        }

    semantic_engine._lazy_load()

    write_event(
        kind="semantic_init",
        subsystem="semantic",
        state="loaded",
        revision="B16.2",
        confidence=0.95,
        details={
            "model": SEMANTIC_STATE.model_name,
            "embedding_dim": SEMANTIC_STATE.embedding_dim,
            "forced": force,
        },
    )

    return {
        "status": "ok",
        "loaded": True,
        "model": SEMANTIC_STATE.model_name,
        "embedding_dim": SEMANTIC_STATE.embedding_dim,
    }
