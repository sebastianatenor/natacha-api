"""
Action Whitelist — AGENTE_VERAZ
"""

ALLOWED_ACTIONS = {
    "automation": [
        "print_status",
    ]
}


def is_action_allowed(domain: str, action: str) -> bool:
    return action in ALLOWED_ACTIONS.get(domain, [])
