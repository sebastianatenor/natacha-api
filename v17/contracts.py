# v17/contracts.py

from dataclasses import dataclass
from typing import Optional, Literal, List


# =========================
# SEMANTIC
# =========================
@dataclass(frozen=True)
class SemanticFrame:
    text: str
    intent: str
    risk_level: str
    confidence: float
    domains: List[str]
    fingerprint: str


# =========================
# GATE
# =========================
@dataclass(frozen=True)
class GateDecision:
    blocked: bool
    reason: str


# =========================
# SYSTEM
# =========================
@dataclass(frozen=True)
class SystemDecision:
    semantic: SemanticFrame
    gate: GateDecision
    required_action: Optional[Literal["human_decision"]]
