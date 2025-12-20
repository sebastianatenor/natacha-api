from ops.timeline.reader import read_events

def build_timeline():
    events = read_events()

    semantic_loaded = any(
        e.get("kind") == "cognitive_state"
        and e.get("subsystem") == "semantic"
        and e.get("state") == "loaded"
        for e in events
    )

    checkpoints = [e for e in events if e.get("kind") == "self_checkpoint"]
    snapshots = [e for e in events if e.get("kind") == "daily_snapshot"]

    derived = {
        "semantic_loaded": semantic_loaded,
        "checkpoint_count": len(checkpoints),
        "snapshot_count": len(snapshots),
        "maturity": (
            "high"
            if semantic_loaded and len(snapshots) >= 1
            else "developing"
        )
    }

    return {
        "events": events[-50:],  # ventana reciente
        "derived_state": derived
    }
