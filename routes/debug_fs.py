# routes/debug_fs.py

from fastapi import APIRouter
from pathlib import Path
import os

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/fs")
def debug_fs():
    base = Path("/app")
    docs = base / "docs"
    manifests = docs / "manifests"

    return {
        "cwd": os.getcwd(),
        "base_exists": base.exists(),
        "docs_exists": docs.exists(),
        "manifests_exists": manifests.exists(),
        "docs_files": [p.name for p in docs.iterdir()] if docs.exists() else [],
        "manifests_files": [p.name for p in manifests.iterdir()] if manifests.exists() else [],
    }
