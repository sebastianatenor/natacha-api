# v17/system/router_shadow.py

from fastapi import APIRouter
from pydantic import BaseModel

from v17.system.orchestrator_shadow import orchestrate_with_shadow

router = APIRouter(prefix="/v17/system", tags=["v17", "shadow"])


class OrchestratePayload(BaseModel):
    text: str


@router.post("/orchestrate_shadow")
def orchestrate_shadow(payload: OrchestratePayload):
    decision = orchestrate_with_shadow(payload.text)

    return {
        "semantic": {
            "intent": decision.semantic.intent,
            "risk_level": decision.semantic.risk_level,
            "confidence": decision.semantic.confidence,
            "domains": decision.semantic.domains,
        },
        "gate": {
            "blocked": decision.gate.blocked,
            "reason": decision.gate.reason,
        },
        "required_action": decision.required_action,
        "engine": "v17",
        "mode": "shadow",
    }
