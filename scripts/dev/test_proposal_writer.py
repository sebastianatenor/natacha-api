# scripts/dev/test_proposal_writer.py
import sys
from pathlib import Path

# Fix PYTHONPATH
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.cognitive.proposals.reasoner import generate_proposals
from ops.cognitive.proposals.writer import write_proposals_bulk
from ops.system.perception_provider import read_system_perception
from ops.timeline.reader import read_events

print("=== B13 Proposal Writer Test ===")

perception = read_system_perception()

# Build minimal system status from timeline (B12 canonical)
events = read_events()
system_status = {
    "runtime": {
        "revision": perception.get("revision"),
    },
    "memory": {
        "items_count": len(events),
    },
}

proposals = generate_proposals(perception, system_status)

print(f"Generated {len(proposals)} proposals")

if not proposals:
    print("Nothing to write")
    exit(0)

for i, p in enumerate(proposals, 1):
    print(f"{i}. {p.get('summary')}")

confirm = input("Write proposals to timeline? (yes/no): ").strip().lower()

if confirm == "yes":
    written = write_proposals_bulk(proposals)
    print(f"{len(written)} proposals written")
else:
    print("Aborted")
