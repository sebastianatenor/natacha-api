from ops.timeline.reader import read_events


def search_memory(query: str, limit: int = 20):
    query_lc = query.lower()
    results = []

    for ev in read_events():
        if ev.get("kind") != "memory_note":
            continue

        content = ev.get("content", "").lower()
        tags = " ".join(ev.get("tags", [])).lower()

        if query_lc in content or query_lc in tags:
            results.append(ev)

    return results[-limit:]

