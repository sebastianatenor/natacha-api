# ops/cognitive/runtime/manifest_loader.py

from pathlib import Path
from typing import Dict, List

# ============================================================
# MANIFEST ROOT (path absoluto, seguro en Cloud Run)
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]
MANIFEST_DIR = BASE_DIR / "docs" / "manifests"


class ManifestLoader:
    """
    Carga y expone manifiestos cognitivos activos.
    Los manifiestos son contratos, no lógica ejecutable.
    """

    def __init__(self, manifest_dir: Path = MANIFEST_DIR):
        self.manifest_dir = manifest_dir
        self._cache: Dict[str, str] = {}

    def load_all(self) -> Dict[str, str]:
        manifests: Dict[str, str] = {}

        if not self.manifest_dir.exists():
            return {}

        for file in sorted(self.manifest_dir.glob("*.md")):
            manifests[file.name] = file.read_text(encoding="utf-8")

        self._cache = manifests
        return manifests

    def list_names(self) -> List[str]:
        if not self._cache:
            self.load_all()
        return list(self._cache.keys())

    def get(self, name: str) -> str:
        if not self._cache:
            self.load_all()
        return self._cache.get(name, "")
