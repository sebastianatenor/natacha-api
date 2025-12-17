# routes/natacha_routes.py

from fastapi import APIRouter, HTTPException, Body, Request
from typing import Dict, Any

router = APIRouter(prefix="/natacha", tags=["natacha"])


@router.post("/chat")
async def natacha_chat(
    request: Request,
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Alias HTTP de /agent/interact
    Evita imports circulares.
    """

    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message'")

    # Reenviamos al handler real vía ASGI
    scope = request.scope.copy()
    scope["path"] = "/agent/interact"
    scope["raw_path"] = b"/agent/interact"
    scope["method"] = "POST"

    receive = request.receive
    send_events = []

    async def send(message):
        send_events.append(message)

    await request.app(scope, receive, send)

    # Buscar respuesta HTTP
    for event in send_events:
        if event["type"] == "http.response.body":
            return {
                "ok": True,
                "response": event.get("body", b"").decode()
            }

    raise HTTPException(
        status_code=500,
        detail="Agent interact did not return a response"
    )
