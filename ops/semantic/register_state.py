from fastapi import APIRouter

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])

@router.post("/register-loaded")
def register_semantic_loaded():
    # Import lazy (Cloud Run safe)
    from ops.cognitive.auto_checkpoint import write_cognitive_state

    write_cognitive_state(
        subsystem="semantic",
        state="loaded",
        confidence="high"
    )

    return {
        "status": "ok",
        "semantic_state": "registered"
    }
