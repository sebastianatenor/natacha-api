def compute_system_state():
    return {
        "engine": "v17",
        "mode": "shadow",
        "semantic": "heuristic",
        "memory": {
            "timeline": "active",
            "snapshots": "enabled",
            "checkpoints": "enabled",
        },
        "ml": {
            "training": "disabled",
            "shadow_collection": "active",
        }
    }
