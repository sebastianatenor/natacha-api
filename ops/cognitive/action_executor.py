"""
Action Executor — AGENTE_VERAZ
"""

from typing import Dict
from ops.cognitive.action_whitelist import is_action_allowed
from ops.timeline.action_writer import write_action_event


def execute_confirmed_action(signal: Dict) -> Dict:
    domain = signal.get("domains", [None])[0]
    action = "print_status"

    if not is_action_allowed(domain, action):
        result = {
            "executed": False,
            "reason": "action_not_whitelisted",
            "domain": domain,
            "action": action,
        }
    else:
        # 🔥 ACCIÓN REAL (CONTROLADA)
        print("[EXECUTION] Acción real ejecutada:", action)

        result = {
            "executed": True,
            "action": action,
            "domain": domain,
        }

    write_action_event(
        kind="action_execution",
        signal=signal,
        result=result,
    )

    return result
