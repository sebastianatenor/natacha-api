# v17/system/orchestrator_shadow.py

from v17.system.orchestrator import orchestrate
from ops.timeline.write_shadow_ml import write_shadow_ml_event
from ops.semantic.semantic_linker import link_semantic

link_semantic(
    reference=text,
    domains=decision.semantic.domains
)


def orchestrate_with_shadow(text: str):
    decision = orchestrate(text)

    write_shadow_ml_event({
        "text": text,
        "semantic": {
            "intent": decision.semantic.intent,
            "risk_level": decision.semantic.risk_level,
            "confidence": decision.semantic.confidence,
            "domains": decision.semantic.domains,
        },
        "gate": {
            "blocked": decision.gate.blocked,
            "reason": decision.gate.reason,
        },
        "required_action": decision.required_action,
        "engine": "v17",
        "mode": "shadow",
    })

    return decision
