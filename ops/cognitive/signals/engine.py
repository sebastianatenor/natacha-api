from typing import List, Dict, Any
from .model import CognitiveSignal
from .extractors import extract_semantic_signals, extract_memory_signals

def collect_signals(
    perception: Dict[str, Any],
    status: Dict[str, Any],
) -> List[CognitiveSignal]:
    signals: List[CognitiveSignal] = []
    signals += extract_semantic_signals(perception)
    signals += extract_memory_signals(status)
    return signals
