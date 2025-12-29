def compute_system_state():
    return {
        "engine": "v17",
        "mode": "shadow",
        "semantic": {
            "status": "heuristic",
            "vector": "disabled",
        },
        "memory": {
            "timeline": "active",
            "snapshots": "enabled",
            "checkpoints": "enabled",
        },
        "ml": {
            "shadow_collection": "active",
            "training": "disabled",
        }
    }
