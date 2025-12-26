import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.timeline.reader import read_events
from routes.system_generate_proposal import generate_and_persist_proposals
from routes.system_proposal_lifecycle import accept_proposal
from routes.system_proposals import list_proposals

print("=== B14.5 Lifecycle Test ===")

generate_and_persist_proposals()
proposals = list_proposals(limit=1)["proposals"]
assert proposals, "No proposals found"

pid = proposals[-1]["event_id"]
print("Proposal ID:", pid)

res = accept_proposal(
    proposal_id=pid,
    payload={"actor": "tester", "rationale": "Looks correct"},
)
print("Accept:", res)

events = read_events()
states = [
    e["details"]["new_state"]
    for e in events
    if e.get("kind") == "cognitive_proposal_lifecycle"
    and e["details"]["proposal_id"] == pid
]

print("Lifecycle states:", states)
