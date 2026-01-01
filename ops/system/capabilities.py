# ops/system/capabilities.py
# Declarative Cognitive Capability Registry
# No execution logic. Source of truth only.

COGNITIVE_CAPABILITIES = {
    "core_service": "natacha-os-v7",

    "agent": {
        "interact": {
            "module": "ops.agent.interact",
            "entrypoint": "/agent/interact",
            "status": "active",
            "authoritative": True
        }
    },

    "cognitive_modules": {
        "affective": "active",
        "predictive": "active",
        "context": "active"
    },

    "semantic": {
        "mode": "heuristic_only",
        "write": False,
        "learning": False,
        "vector": False,
        "status": "active"
    },

    "memory": {
        "persistent": True,
        "temporal": True,
        "vector": False
    },

    "tasks": {
        "execution": "delegated",
        "service": "natacha-tasks-service"
    }
}
