# ops/timeline/write_shadow_ml.py

from ops.timeline.writer import write_event


def write_shadow_ml_event(payload: dict):
    """
    Shadow ML logging (NO side effects)

    Adapta el payload v17 al contrato estable del timeline.
    """

    write_event(
        kind="shadow_ml_sample",
        subsystem="v17",
        state="observed",
        revision=payload.get("engine", "v17"),
        confidence=payload.get("semantic", {}).get("confidence", 0.0),
        details=payload,
    )
