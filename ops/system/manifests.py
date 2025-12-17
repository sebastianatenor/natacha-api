# ops/system/manifests.py

from fastapi import APIRouter
from pathlib import Path

router = APIRouter(
    prefix="/ops/manifests",
    tags=["manifests"]
)

MANIFEST_DIR = Path("docs/manifests")


@router.get("/list")
def list_manifests():
    """
    Lista TODOS los manifiestos cognitivos disponibles en runtime.
    (Modelo simple: todo manifiesto presente es activo)
    """
    if not MANIFEST_DIR.exists():
        return {
            "active_manifests": [],
            "error": "manifest_dir_not_found"
        }

    manifests = sorted(
        f.name for f in MANIFEST_DIR.glob("*.md")
    )

    return {
        "active_manifests": manifests,
        "count": len(manifests)
    }
