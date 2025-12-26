import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.system.perception_provider import read_system_perception
from ops.timeline.reader import read_events
from ops.cognitive.signals.engine import collect_signals
from ops.cognitive.proposals.mapper import proposals_from_signals

print("=== B14.2 Signal → Proposal Test ===")

perception = read_system_perception()
events = read_events()

system_status = {
    "timeline_events": len(events),
}

signals = collect_signals(perception, system_status)
proposals = proposals_from_signals(
    signals,
    source_revision="B14.2-dev"
)

print(f"Signals: {len(signals)}")
print(f"Proposals: {len(proposals)}")

for i, p in enumerate(proposals, 1):
    print(f"{i}. [{p['priority']}] {p['title']}")
