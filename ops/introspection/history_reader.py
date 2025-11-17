"""
ops.introspection.history_reader
---------------------------------
Lee y analiza introspecciones previas guardadas en memory_store.jsonl.
Permite a Natacha reflexionar sobre la evolución de su propio código.
"""

import json
from pathlib import Path
from collections import Counter
from fastapi import APIRouter

router = APIRouter(prefix="/ops/introspection", tags=["Introspection"])

MEMORY_PATH = Path("memory_store.jsonl")


@router.get("/history")
def read_introspection_history(limit: int = 10):
    """Lee las introspecciones previas y analiza su contenido."""
    if not MEMORY_PATH.exists():
        return {"status": "error", "message": "memory_store.jsonl no encontrado"}

    entries = []
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("kind") == "introspection_result":
                    entries.append(entry)
            except json.JSONDecodeError:
                continue

    if not entries:
        return {"status": "empty", "message": "No hay introspecciones registradas"}

    # Últimas introspecciones
    latest = entries[-limit:]

    # Estadísticas
    issue_counts = [len(e["detail"].get("issues", [])) for e in latest if "detail" in e]
    avg_issues = sum(issue_counts) / len(issue_counts) if issue_counts else 0

    # Archivos más repetidos
    all_files = []
    for e in latest:
        for issue in e["detail"].get("issues", []):
            all_files.append(issue["file"])
    top_files = Counter(all_files).most_common(5)

    summary = {
        "entries_analyzed": len(latest),
        "average_issues_per_run": round(avg_issues, 2),
        "most_repeated_files": top_files,
    }

    return {
        "status": "ok",
        "summary": summary,
        "latest_entries": latest[-3:],  # muestra las últimas 3 introspecciones
    }

@router.get("/compare")
def compare_versions():
    """Compara la cantidad de issues entre versiones."""
    path = Path("memory_store.jsonl")
    if not path.exists():
        return {"status": "error", "message": "memory_store.jsonl no encontrado"}

    data = [json.loads(line) for line in path.open() if '"introspection_result"' in line]
    if not data:
        return {"status": "error", "message": "sin introspecciones previas"}

    by_version = {}
    for entry in data:
        v = entry["detail"].get("version", "unknown")
        count = len(entry["detail"].get("issues", []))
        by_version.setdefault(v, []).append(count)

    summary = {v: sum(c) / len(c) for v, c in by_version.items()}

    return {
        "status": "ok",
        "trend": "improving" if list(summary.values())[-1] < list(summary.values())[0] else "stable_or_worse",
        "summary": summary,
    }
