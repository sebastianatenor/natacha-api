import sys
from pathlib import Path

# --- asegurar root del proyecto ---
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ops.system.perception_provider import read_system_perception
from ops.timeline.reader import read_events
from ops.cognitive.signals.engine import collect_signals

print("=== B14.1 Signal Test ===")

perception = read_system_perception()

# system_status CANÓNICO viene del timeline
events = read_events()
system_status = {
    "timeline_events": len(events),
    "last_event_kind": events[-1]["kind"] if events else None,
}

signals = collect_signals(perception, system_status)

if not signals:
    print("No signals generated.")
else:
    for s in signals:
        print(
            f"- {s.type} | severity={s.severity} | confidence={s.confidence}"
        )

print("TOTAL SIGNALS:", len(signals))
