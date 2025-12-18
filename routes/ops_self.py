from fastapi import APIRouter, Query
import os, json, subprocess, datetime, pathlib

from ops.memory.manager import user_context_manager

router = APIRouter()


def _git_rev():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return os.getenv("REVISION", "unknown")


@router.post("/ops/self_register")
def self_register():
    primary = os.getenv("PRIMARY_HOST", "")
    legacy = os.getenv("LEGACY_HOST", "")
    url = os.getenv("SERVICE_URL", f"https://{primary}") if primary else ""

    data = {
        "service": "natacha-api",
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "runtime": {
            "primary": primary,
            "legacy": legacy,
            "url": url,
            "region": os.getenv("REGION", "us-central1"),
            "revision": os.getenv("K_REVISION", _git_rev()),
        },
    }

    # Persistir copia local (versionable)
    p = pathlib.Path("knowledge/registry")
    p.mkdir(parents=True, exist_ok=True)
    (p / "RUNTIME.json").write_text(json.dumps(data, indent=2))

    return {
        "status": "ok",
        "saved": "RUNTIME.json",
        "data": data,
    }


@router.get("/ops/user/state")
def user_state(user_id: str = Query(..., description="User ID")):
    """
    Estado cognitivo vivo (RAM).
    No persistente. No histórico.
    """
    snapshot = user_context_manager.snapshot(user_id)

    return {
        "status": "ok",
        "engine": "live_user_context",
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "data": snapshot,
    }
