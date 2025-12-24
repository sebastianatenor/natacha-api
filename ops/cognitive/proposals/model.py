# ops/cognitive/proposals/model.py
from datetime import datetime
from typing import Dict, Any, Literal
from pydantic import BaseModel


class CognitiveProposal(BaseModel):
    id: str
    timestamp: str
    kind: Literal["action", "system", "memory", "semantic"]
    title: str
    description: str
    rationale: str
    confidence: float
    source_revision: str
    status: Literal["proposed", "accepted", "rejected"] = "proposed"

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat() + "Z"
