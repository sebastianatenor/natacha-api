# ops/cognitive/decisions/model.py

from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime
from typing import Optional


class CognitiveDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    proposal_id: str

    # 🔑 CLAVE B16 FINAL
    fingerprint: str

    decision: str  # accepted | rejected
    reason: Optional[str] = None
    confidence: float = 0.5

    decided_by: str = "human"
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
