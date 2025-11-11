import hashlib, json, os

def stable_key(project: str, title: str, suspect_paths: list[str]) -> str:
    norm = sorted(os.path.normpath(p) for p in suspect_paths)
    payload = json.dumps({"project": project, "title": title, "paths": norm},
                         separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"{project}:{title}:{digest}"

def append_evidence(tasks_col, task_id: str, paths: list[str]):
    # Evita duplicados de paths dentro del array evidence
    tasks_col.update_one(
        {"_id": task_id},
        {"$addToSet": {"evidence": {"$each": sorted(set(paths))}}}
    )
