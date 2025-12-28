# v17/system/router.py

from fastapi import APIRouter
from pydantic import BaseModel

from v17.system.orchestrator import orchestrate

router = APIRouter(prefix="/v17/system", tags=["v17"])


class OrchestratePayload(BaseModel):
    text: str


@router.post("/orchestrate")
def orchestrate_v17(payload: OrchestratePayload):
    decision = orchestrate(payload.text)

    return {
        "semantic": {
            "intent": decision.semantic.intent,
            "risk_level": decision.semantic.risk_level,
            "confidence": decision.semantic.confidence,
            "domains": decision.semantic.domains,
            "fingerprint": decision.semantic.fingerprint,
        },
        "gate": {
            "blocked": decision.gate.blocked,
            "reason": decision.gate.reason,
        },
        "required_action": decision.required_action,
        "engine": "v17",
    }
