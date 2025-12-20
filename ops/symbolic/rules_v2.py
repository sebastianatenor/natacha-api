from typing import Dict, List


def evaluate_system_health(derived_state: Dict) -> List[Dict]:
    """
    Evalúa el estado cognitivo del sistema y devuelve reglas simbólicas
    interpretables por humanos.
    """

    rules = []

    semantic_loaded = derived_state.get("semantic_loaded", False)
    snapshot_count = derived_state.get("snapshot_count", 0)
    maturity = derived_state.get("maturity", "unknown")

    # 🟢 Sistema estable
    if semantic_loaded and snapshot_count >= 1:
        rules.append({
            "rule": "SYSTEM_STABLE",
            "severity": "info",
            "message": "El sistema se encuentra estable con cognición semántica activa y snapshots diarios.",
            "confidence": "high"
        })

    # 🟡 Falta de snapshots
    if snapshot_count == 0:
        rules.append({
            "rule": "NO_DAILY_SNAPSHOTS",
            "severity": "warning",
            "message": "No existen snapshots diarios. Riesgo de pérdida de trazabilidad histórica.",
            "confidence": "medium"
        })

    # 🟡 Semantic no cargado
    if not semantic_loaded:
        rules.append({
            "rule": "SEMANTIC_NOT_LOADED",
            "severity": "warning",
            "message": "La cognición semántica no está cargada. Se recomienda precargar el motor.",
            "confidence": "medium"
        })

    # 🔵 Sistema inmaduro
    if maturity in ("developing", "unknown"):
        rules.append({
            "rule": "SYSTEM_IN_DEVELOPMENT",
            "severity": "info",
            "message": "El sistema se encuentra en etapa de desarrollo cognitivo.",
            "confidence": "medium"
        })

    return rules
