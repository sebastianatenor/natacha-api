# ops/cognitive/proposals/model.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import uuid4


class CognitiveProposal(BaseModel):
    id: str
    timestamp: str

    title: str
    description: str
    rationale: str

    kind: str
    status: str
    confidence: float

    source_revision: str
    source: Optional[str] = None

    # 🔑 B16
    fingerprint: Optional[str] = None

    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def new_id() -> str:
        return str(uuid4())
