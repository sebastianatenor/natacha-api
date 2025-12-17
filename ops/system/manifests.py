# ops/system/manifests.py

from fastapi import APIRouter
from ops.cognitive.runtime.manifest_loader import ManifestLoader

router = APIRouter(
    prefix="/ops/manifests",
    tags=["manifests"]
)

loader = ManifestLoader()


@router.get("/list")
def list_manifests():
    """
    Devuelve la lista de manifiestos cognitivos activos.
    Read-only. No ejecuta lógica.
    """
    return {
        "active_manifests": loader.list_names()
    }


@router.get("/get/{name}")
def get_manifest(name: str):
    """
    Devuelve el contenido completo de un manifiesto.
    Uso: auditoría, debug, UI, verificación humana.
    """
    content = loader.get(name)
    if not content:
        return {
            "error": "manifest_not_found",
            "name": name
        }

    return {
        "name": name,
        "content": content
    }
