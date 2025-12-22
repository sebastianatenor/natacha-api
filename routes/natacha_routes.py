# routes/natacha_routes.py

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any

from ops.agent.interact import agent_interact, AgentInteractRequest

router = APIRouter(prefix="/natacha", tags=["natacha"])


@router.post("/chat")
def natacha_chat(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Entrada pública del agente.
    Ejecuta interacción cognitiva REAL (sin proxy ASGI).
    """

    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message'")

    # Construimos request canónica del agente
    req = AgentInteractRequest(
        user_id=payload.get("user_id", "sebastian"),
        project=payload.get("project", "LLVC"),
        message=message,
    )

    result = agent_interact(req)

    return {
        "ok": True,
        "answer": result.answer,
        "model_called": result.model_called,
        "error": result.error,
        "detail": result.detail,
    }
