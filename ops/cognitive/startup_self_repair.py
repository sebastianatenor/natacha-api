# ops/cognitive/startup_self_repair.py

import os

_ALREADY_RAN = False


def attempt_startup_self_repair():
    global _ALREADY_RAN

    if _ALREADY_RAN:
        return

    # Guardrails duros
    if os.getenv("SELF_REPAIR_ARMED") != "1":
        print("[SELF-REPAIR] Not armed → skipped")
        return

    if os.getenv("COGNITIVE_FREEZE") == "1":
        print("[SELF-REPAIR] Cognitive freeze active → skipped")
        return

    try:
        from routes.system_baseline.provider import read_system_baseline
        from ops.system.perception_provider import read_system_perception
        from ops.cognitive.drift_detector import detect_drift
        from ops.cognitive.repair_executor import execute_repair
    except Exception as e:
        print(f"[SELF-REPAIR][IMPORT ERROR] {e}")
        return

    baseline = read_system_baseline()
    perception = read_system_perception()

    if not baseline or not perception:
        print("[SELF-REPAIR] Baseline or perception unavailable")
        return

    drift = detect_drift(baseline, perception)

    if not drift.get("drift_detected"):
        print("[SELF-REPAIR] No drift detected")
        _ALREADY_RAN = True
        return

    print(f"[SELF-REPAIR] Drift detected → executing repair: {drift}")

    try:
        execute_repair(drift)
        print("[SELF-REPAIR] Repair executed successfully")
    except Exception as e:
        print(f"[SELF-REPAIR][ERROR] {e}")

    _ALREADY_RAN = True

