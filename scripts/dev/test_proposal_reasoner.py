# scripts/dev/test_proposal_reasoner.py

from ops.cognitive.proposals.reasoner import generate_proposals
from ops.system.perception_provider import read_system_perception
from ops.system.full_status_provider import read_full_status

print("=== Running Cognitive Proposal Reasoner (B13.2) ===")

perception = read_system_perception()
status = read_full_status()

proposals = generate_proposals(
    perception=perception,
    status=status,
)

print(f"\nGenerated {len(proposals)} proposals:\n")

for i, p in enumerate(proposals, start=1):
    print(f"{i}. [{p['type']}] ({p['confidence']})")
    print(f"   Summary: {p['summary']}")
    print(f"   Why now: {p['why_now']}")
    print(f"   Details: {p['details']}")
    print()
