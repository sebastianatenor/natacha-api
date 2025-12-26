import json
from ops.timeline.utils import get_timeline_path

def read_events():
    path = get_timeline_path()
    events = []

    try:
        with open(path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                events.append(json.loads(line))
    except FileNotFoundError:
        pass

    return events
