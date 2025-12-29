# ops/system/state_aggregator.py

def compute_system_state():
    return {
        "infra": "stable",
        "cognition": "developing",
        "memory": {
            "persistent": True,
            "semantic": False,
            "snapshots": 0,
        },
        "semantic_engine": "standby",
        "overall_completion": 0.68,
    }
