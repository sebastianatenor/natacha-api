from typing import Dict, List

def evaluate_symbolic_health(derived_state: Dict) -> List[Dict]:
    """
    Evalúa el estado cognitivo del sistema y devuelve
    reglas simbólicas legibles para humanos.
    """

    rules: List[Dict] = []

    semantic_loaded = derived_state.get("semantic_loaded", False)
    snapshot_count = derived_state.get("snapshot_count", 0)
    checkpoint_count = derived_state.get("checkpoint_count", 0)

    # --- Regla: semántica no cargada
    if not semantic_loaded:
        rules.append({
            "rule": "SEMANTIC_NOT_LOADED",
            "confidence": "medium",
            "message": "El motor semántico aún no está cargado."
        })

    # --- Regla: no hay snapshots
    if snapshot_count == 0:
        rules.append({
            "rule": "NO_SNAPSHOTS",
            "confidence": "medium",
            "message": "No hay snapshots diarios registrados."
        })

    # --- Regla: no hay checkpoints
    if checkpoint_count == 0:
        rules.append({
            "rule": "NO_CHECKPOINTS",
            "confidence": "low",
            "message": "No hay checkpoints cognitivos registrados."
        })

    return rules
