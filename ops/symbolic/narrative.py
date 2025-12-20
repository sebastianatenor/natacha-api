from typing import Dict, List


def build_narrative(derived_state: Dict, rules: List[Dict]) -> Dict:
    """
    Construye un diagnóstico narrativo humano a partir del estado cognitivo
    y las reglas simbólicas evaluadas.
    """

    semantic_loaded = derived_state.get("semantic_loaded", False)
    snapshot_count = derived_state.get("snapshot_count", 0)
    maturity = derived_state.get("maturity", "unknown")

    summary_parts = []
    recommendations = []

    # --- Estado general
    if semantic_loaded:
        summary_parts.append("La cognición semántica se encuentra activa.")
    else:
        summary_parts.append("La cognición semántica no está cargada actualmente.")
        recommendations.append(
            "Ejecutar una carga temprana del motor semántico para asegurar comprensión profunda."
        )

    if snapshot_count > 0:
        summary_parts.append(f"Existen {snapshot_count} snapshots diarios registrados.")
    else:
        summary_parts.append("No hay snapshots diarios registrados.")
        recommendations.append(
            "Asegurar la ejecución automática del snapshot diario para preservar memoria histórica."
        )

    if maturity == "high":
        summary_parts.append("El sistema presenta un nivel de madurez cognitiva alto.")
    elif maturity == "developing":
        summary_parts.append("El sistema se encuentra en una etapa de desarrollo cognitivo.")
        recommendations.append(
            "Continuar reforzando reglas simbólicas y persistencia histórica."
        )
    else:
        summary_parts.append("El nivel de madurez cognitiva es desconocido.")

    # --- Severidad global
    severity = "stable"
    for rule in rules:
        if rule.get("severity") == "warning":
            severity = "attention_required"
            break

    return {
        "severity": severity,
        "summary": " ".join(summary_parts),
        "recommendations": recommendations,
        "rules_evaluated": rules,
        "confidence": "high" if severity == "stable" else "medium"
    }
