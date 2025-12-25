# scripts/dev/test_proposal_pipeline.py
import sys
from pathlib import Path

# 🔧 Bootstrap del proyecto (B13)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from ops.cognitive.proposals.reasoner import generate_proposals
from ops.cognitive.proposals.writer import write_proposals_bulk
from ops.system.perception_provider import read_system_perception
from routes.system_full_status import system_full_status

print("=== B13.4 Proposal Pipeline Test ===")

# --- Read-only inputs ---
perception = read_system_perception()
status = system_full_status()

# --- Generate proposals (NO side effects) ---
proposals = generate_proposals(perception, status)

print(f"\nGenerated {len(proposals)} proposals\n")

# --- Display proposals (aligned with CognitiveProposal model) ---
for i, p in enumerate(proposals, 1):
    print(
        f"{i}. [{p.get('priority')}] "
        f"{p.get('title')} "
        f"(confidence={p.get('confidence')})"
    )

if not proposals:
    print("\nNothing to write.")
    sys.exit(0)

confirm = input("\nWrite proposals to timeline? (yes/no): ").strip().lower()

if confirm == "yes":
    written = write_proposals_bulk(proposals)
    print(f"\n{len(written)} proposals written.")
else:
    print("\nAborted.")
