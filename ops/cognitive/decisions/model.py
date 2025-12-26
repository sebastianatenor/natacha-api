# ops/cognitive/decisions/model.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


DecisionState = Literal["accepted", "rejected", "deferred"]


class CognitiveDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str

    decision: DecisionState
    reason: Optional[str] = None

    decided_by: str = "human"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    confidence: Optional[float] = None
