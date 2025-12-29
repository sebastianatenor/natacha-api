from ops.timeline.writer import write_event

def link_semantic(reference: str, domains: list[str]):
    write_event(
        kind="semantic_link",
        subsystem="semantic",
        state="linked",
        revision="v17",
        confidence=0.6,
        details={
            "reference": reference,
            "domains": domains,
        }
    )
