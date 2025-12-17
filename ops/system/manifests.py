# ops/system/manifests.py

from fastapi import APIRouter
from pathlib import Path
import re

router = APIRouter(
    prefix="/ops/manifests",
    tags=["manifests"]
)

REGISTRY_PATH = Path("docs/REGISTRY.md")


def _load_active_manifests_from_registry():
    """
    Lee el REGISTRY.md y extrae la sección:
    '## Active Cognitive Constitution'
    """
    if not REGISTRY_PATH.exists():
        return []

    text = REGISTRY_PATH.read_text(encoding="utf-8")

    # Buscar bloque "Active Cognitive Constitution"
    match = re.search(
        r"## Active Cognitive Constitution.*?\n(.*?)\n\n",
        text,
        re.S
    )

    if not match:
        return []

    block = match.group(1)

    manifests = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("-"):
            name = line.lstrip("-").strip()
            if not name.endswith(".md"):
                name = f"{name}.md"
            manifests.append(name)

    return manifests


@router.get("/list")
def list_manifests():
    """
    Devuelve SOLO los manifiestos activos según REGISTRY.md.
    """
    return {
        "active_manifests": _load_active_manifests_from_registry()
    }


@router.get("/get/{name}")
def get_manifest(name: str):
    """
    Devuelve el contenido de un manifiesto SOLO si está activo.
    """
    active = _load_active_manifests_from_registry()

    if name not in active:
        return {
            "error": "manifest_not_active",
            "name": name
        }

    path = Path("docs/manifests") / name
    if not path.exists():
        return {
            "error": "manifest_file_not_found",
            "name": name
        }

    return {
        "name": name,
        "content": path.read_text(encoding="utf-8")
    }
