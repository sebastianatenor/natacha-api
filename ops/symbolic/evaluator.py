from ops.timeline.builder import build_timeline
from ops.symbolic.rules import evaluate_rules

def evaluate():
    timeline = build_timeline()
    rules = evaluate_rules(timeline["derived_state"])

    return {
        "derived_state": timeline["derived_state"],
        "symbolic_evaluation": rules
    }
