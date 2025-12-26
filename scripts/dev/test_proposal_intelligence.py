import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.system.perception_provider import read_system_perception
from ops.timeline.reader import read_events
from ops.cognitive.signals.engine import collect_signals
from ops.cognitive.proposals.mapper import proposals_from_signals
from ops.cognitive.proposals.intelligence import enrich_and_dedup

print("=== B14.3 Proposal Intelligence Test ===")

perception = read_system_perception()
events = read_events()

signals = collect_signals(
    perception,
    {"timeline_events": len(events)}
)

raw = proposals_from_signals(
    signals,
    source_revision="B14.3-dev"
)

final = enrich_and_dedup(raw)

print(f"Signals: {len(signals)}")
print(f"Raw proposals: {len(raw)}")
print(f"Final proposals: {len(final)}\n")

for i, p in enumerate(final, 1):
    print(
        f"{i}. [{p['priority']}] "
        f"{p['title']} | score={p['score']} | conf={p['confidence']}"
    )
