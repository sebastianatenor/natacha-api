from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CognitiveSignal(BaseModel):
    type: str                     # ej: semantic_inactive, memory_growth
    severity: str                 # low | medium | high
    confidence: float             # 0..1
    source: str                   # perception | system | timeline
    evidence: Dict[str, Any]      # datos crudos
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    note: Optional[str] = None
