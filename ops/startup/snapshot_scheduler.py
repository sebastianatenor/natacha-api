import threading
import time
from ops.system.snapshot_engine import create_snapshot

def snapshot_loop():
    while True:
        time.sleep(60 * 60 * 24)
        create_snapshot(reason="daily")

def start_snapshot_scheduler():
    t = threading.Thread(target=snapshot_loop, daemon=True)
    t.start()
