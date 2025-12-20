from typing import List, Dict, Any


# =====================================================
# DERIVED STATE
# =====================================================
def derive_state_from_events(events: List[Dict]) -> Dict[str, Any]:
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


# =====================================================
# LOW-LEVEL NARRATIVE (internal)
# =====================================================
def build_cognitive_narrative(
    *,
    derived_state: Dict[str, Any],
    rules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    summary = "El sistema se encuentra en una etapa de desarrollo cognitivo."
    if derived_state.get("maturity") == "high":
        summary = "El sistema presenta un nivel de madurez cognitiva alto."

    recommendations: List[str] = []

    for r in rules:
        if r.get("rule") == "SEMANTIC_NOT_LOADED":
            recommendations.append(
                "Ejecutar una carga temprana del motor semántico para asegurar comprensión profunda."
            )

    return {
        "summary": summary,
        "recommendations": recommendations,
        "confidence": "high",
    }


# =====================================================
# PUBLIC API (⚠️ ESTE ES EL QUE FALTABA)
# =====================================================
def build_narrative(
    *,
    derived_state: Dict[str, Any],
    symbolic_rules: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    API pública consumida por routes.system_diagnose

    Mantiene compatibilidad futura y encapsula la narrativa cognitiva.
    """

    narrative = build_cognitive_narrative(
        derived_state=derived_state,
        rules=symbolic_rules,
    )

    return {
        "severity": "stable",
        "summary": narrative["summary"],
        "recommendations": narrative["recommendations"],
        "rules_evaluated": symbolic_rules,
        "confidence": narrative.get("confidence", "high"),
    }
