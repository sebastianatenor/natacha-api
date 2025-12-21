from typing import Dict, List


def derive_state_from_events(events: List[Dict]) -> Dict:
    semantic_loaded = False
    snapshot_count = 0
    checkpoint_count = 0

    for e in events:
        if e.get("kind") == "cognitive_state" and e.get("subsystem") == "semantic":
            if e.get("state") == "loaded":
                semantic_loaded = True

        if e.get("kind") == "daily_snapshot":
            snapshot_count += 1

        if e.get("kind") == "self_checkpoint":
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


def build_narrative(
    *,
    derived_state: Dict,
    rules: List[Dict],
) -> Dict:
    """
    Construye una narrativa cognitiva humana a partir del estado derivado
    y las reglas simbólicas evaluadas.
    """

    severity = "stable"
    summary = "El sistema se encuentra en una etapa de desarrollo cognitivo."
    recommendations: List[str] = []

    if derived_state.get("maturity") == "high":
        summary = "El sistema presenta un nivel de madurez cognitiva alto."

    for r in rules:
        if r.get("rule") == "SEMANTIC_NOT_LOADED":
            recommendations.append(
                "Ejecutar una carga temprana del motor semántico para asegurar comprensión profunda."
            )

    return {
        "severity": severity,
        "summary": summary,
        "recommendations": recommendations,
        "rules_evaluated": rules,
        "confidence": "high",
    }
