def evaluate_rules(state):
    results = []

    if (
        state["semantic_loaded"]
        and state["checkpoint_count"] >= 1
        and state["snapshot_count"] >= 1
    ):
        results.append({
            "rule": "SYSTEM_MATURE",
            "confidence": "high",
            "message": "Sistema cognitivo maduro y estable"
        })

    if state["snapshot_count"] == 0:
        results.append({
            "rule": "NO_SNAPSHOTS",
            "confidence": "medium",
            "message": "No hay snapshots diarios"
        })

    return results
