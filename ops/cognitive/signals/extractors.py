from typing import List, Dict, Any
from .model import CognitiveSignal

def extract_semantic_signals(perception: Dict[str, Any]) -> List[CognitiveSignal]:
    out: List[CognitiveSignal] = []
    semantic = perception.get("semantic", {})
    if not semantic.get("loaded", False):
        out.append(CognitiveSignal(
            type="semantic_inactive",
            severity="medium",
            confidence=0.7,
            source="perception",
            evidence={"semantic": semantic},
            note="Semantic engine not loaded"
        ))
    return out

def extract_memory_signals(status: Dict[str, Any]) -> List[CognitiveSignal]:
    out: List[CognitiveSignal] = []
    memory = status.get("memory", {})
    items = memory.get("items_count", 0)
    if items >= 3000:
        out.append(CognitiveSignal(
            type="memory_growth",
            severity="low",
            confidence=0.6,
            source="system",
            evidence={"items_count": items},
            note="Memory store growing"
        ))
    return out
