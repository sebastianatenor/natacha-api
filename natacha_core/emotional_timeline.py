import json, os, datetime

TIMELINE_PATH = "data/emotional_timeline.jsonl"

def log_emotion_state(entry: dict):
    """Registra una entrada emocional en la línea temporal."""
    os.makedirs("data", exist_ok=True)
    entry["timestamp"] = datetime.datetime.utcnow().isoformat()
    with open(TIMELINE_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_timeline(limit=20):
    if not os.path.exists(TIMELINE_PATH):
        return []
    with open(TIMELINE_PATH) as f:
        lines = f.readlines()[-limit:]
    return [json.loads(l) for l in lines]
