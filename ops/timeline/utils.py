import os

TIMELINE_LOCAL = "/tmp/natacha_timeline.jsonl"
TIMELINE_GCS_BUCKET = "natacha-memory-store"
TIMELINE_GCS_OBJECT = "timeline.jsonl"

def get_timeline_path():
    return TIMELINE_LOCAL
