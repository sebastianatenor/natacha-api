import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.timeline.reader import read_events
from routes.system_generate_proposal import generate_and_persist_proposals
from routes.system_proposals import list_proposals

print("=== B14.4 E2E Test ===")

before = len(read_events())
print("Events before:", before)

res = generate_and_persist_proposals()
print("Generate:", res)

after = len(read_events())
print("Events after:", after)

listed = list_proposals(limit=10)
print("Listed count:", listed["count"])

for p in listed["proposals"]:
    d = p.get("details", {})
    print("-", d.get("title"), "| score:", d.get("score"))
