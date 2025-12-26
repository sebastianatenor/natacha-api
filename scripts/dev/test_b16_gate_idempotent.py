# scripts/dev/test_b16_gate_idempotent.py

from ops.semantic.engine import get_engine
from ops.semantic.gate import semantic_gate
from ops.cognitive.decisions.writer import write_decision
from ops.cognitive.decisions.model import CognitiveDecision
from ops.timeline.reader import read_events
from ops.semantic.fingerprint import semantic_fingerprint

TEXT = "hacelo automaticamente sin preguntar"

def test_gate_idempotent():
    engine = get_engine()
    assert engine is not None, "Semantic engine not available"

    # 1) Primera pasada → bloquea y crea proposal
    analysis = engine.analyze(TEXT)
    gate1 = semantic_gate(analysis, source="test.b16")

    assert gate1 is not None
    assert gate1["gate"] == "blocked"

    proposal_id = gate1["proposal_id"]   # 👈 ESTA ES LA LÍNEA CLAVE
    fingerprint = semantic_fingerprint(analysis)
    
    print("Blocked with proposal:", gate1["proposal_id"])

    # 2) Aceptar proposal (decisión humana)
    decision = CognitiveDecision(
        proposal_id=proposal_id,
        fingerprint=fingerprint,
        decision="accepted",
        reason="Approved by human",
        confidence=0.9,
    )
    write_decision(decision)

    # 3) Segunda pasada → DEBE permitir
    gate2 = semantic_gate(analysis, source="test.b16")

    assert gate2 is not None
    assert gate2["gate"] == "allowed"
    assert gate2["proposal_id"] == proposal_id
    
    print("Allowed with same proposal:", proposal_id)

    # 4) Verificar que NO se creó proposal nueva
    events = read_events()
    proposals = [
        e for e in events
        if e.get("kind") == "cognitive_proposal"
    ]

    assert len(proposals) == 1, f"Expected 1 proposal, got {len(proposals)}"

    print("PASS: Gate is idempotent")

if __name__ == "__main__":
    test_gate_idempotent()
