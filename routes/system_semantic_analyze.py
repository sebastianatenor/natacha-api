# routes/system_semantic_analyze.py

from fastapi import APIRouter
from pydantic import BaseModel

from ops.semantic import get_engine, semantic_status
from ops.semantic.gate import semantic_gate

from ops.cognitive.approval_cache import (
    proposal_fingerprint,
    find_recent_decision,
)

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


class SemanticRequest(BaseModel):
    text: str


@router.post("/analyze")
def semantic_analyze(payload: SemanticRequest):
    engine = get_engine()

    if engine is None:
        return {
            "status": "disabled",
            "semantic": None,
            "engine": semantic_status(),
        }

    analysis = engine.analyze(payload.text)

    # -------------------------------------------------
    # B16.5 — Approval cache (deduplicación)
    # -------------------------------------------------
    fingerprint = proposal_fingerprint(
        text=payload.text,
        intent=analysis.signals.intent,
        risk=analysis.signals.risk_level,
        domains=analysis.signals.domains,
    )

    cached = find_recent_decision(fingerprint)
    if cached:
        return {
            "status": "ok",
            "semantic": analysis.dict(),
            "gate": {
                "gate": (
                    "approved_cached"
                    if cached["decision"] == "accepted"
                    else "blocked_cached"
                ),
                "reason": "recent_human_decision",
                "decision": cached["decision"],
            },
            "engine": semantic_status(),
        }

    # -------------------------------------------------
    # Gate normal (crea proposal si corresponde)
    # -------------------------------------------------
    gate_result = semantic_gate(
        analysis=analysis,
        source="ops.semantic.analyze",
        fingerprint=fingerprint,  # 👈 pasa fingerprint
    )

    return {
        "status": "ok",
        "semantic": analysis.dict(),
        "gate": gate_result,
        "engine": semantic_status(),
    }
