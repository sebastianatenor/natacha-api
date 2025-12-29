# v17/system/router_shadow.py

from fastapi import APIRouter
from pydantic import BaseModel

from v17.system.orchestrator_shadow import orchestrate_with_shadow

router = APIRouter(prefix="/v17/system", tags=["v17", "shadow"])


class OrchestratePayload(BaseModel):
    text: str


@router.post("/orchestrate_shadow")
def orchestrate_shadow(payload: OrchestratePayload):
    try:
        decision = orchestrate_with_shadow(payload.text)

        return {
            "semantic": decision.semantic.model_dump(),
            "gate": decision.gate.model_dump(),
            "required_action": decision.required_action,
            "engine": "v17",
            "mode": "shadow",
        }

    except Exception as e:
        return {
            "error": "shadow_failed",
            "detail": str(e),
            "engine": "v17",
            "mode": "shadow",
        }
