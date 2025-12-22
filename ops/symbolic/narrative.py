from typing import Dict, List


def derive_state_from_events(events: List[Dict]) -> Dict:
    semantic_loaded = False
    snapshot_count = 0
    checkpoint_count = 0

    for e in events:
        if e.get("kind") == "cognitive_state" and e.get("subsystem") == "semantic":
            if e.get("state") == "loaded":
                semantic_loaded = True
        elif e.get("kind") == "daily_snapshot":
            snapshot_count += 1
        elif e.get("kind") == "self_checkpoint":
            checkpoint_count += 1

    maturity = "developing"
    if semantic_loaded and snapshot_count > 0:
        maturity = "high"

    return {
        "semantic_loaded": semantic_loaded,
        "snapshot_count": snapshot_count,
        "checkpoint_count": checkpoint_count,
        "maturity": maturity,
    }


def build_narrative(*, derived_state: Dict, rules: List[Dict]) -> Dict:
    maturity = derived_state.get("maturity", "developing")

    if maturity == "high":
        summary = "El sistema presenta un nivel de madurez cognitiva alto."
    else:
        summary = "El sistema se encuentra en una etapa de desarrollo cognitivo."

    recommendations = []
    for r in rules:
        if r.get("rule") == "SEMANTIC_NOT_LOADED":
            recommendations.append(
                "Ejecutar una carga temprana del motor semántico."
            )

    return {
        "severity": "stable",
        "summary": summary,
        "recommendations": recommendations,
        "rules_evaluated": rules,
        "confidence": "high",
    }
