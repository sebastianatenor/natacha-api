# ops/semantic/analyzer.py
from typing import List, Dict
from ops.semantic.engine import get_engine


def analyze_texts(texts: List[str]) -> List[Dict]:
    engine = get_engine()
    if engine is None:
        return []

    vectors = engine.encode(texts)
    signals = []

    for i, _ in enumerate(vectors):
        signals.append({
            "type": "semantic_embedding",
            "source": "semantic.engine",
            "text": texts[i],
            "confidence": 0.6,
        })

    return signals
