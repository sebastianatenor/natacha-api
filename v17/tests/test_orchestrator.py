# v17/tests/test_orchestrator.py

from v17.system.orchestrator import orchestrate


def test_high_risk_is_blocked():
    decision = orchestrate("hacelo automaticamente sin preguntar")

    assert decision.gate.blocked is True
    assert decision.required_action == "human_decision"


def test_safe_text_is_allowed():
    decision = orchestrate("hola")

    assert decision.gate.blocked is False
    assert decision.required_action is None
