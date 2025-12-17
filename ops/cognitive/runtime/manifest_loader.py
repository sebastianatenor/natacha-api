# ops/cognitive/runtime/manifest_loader.py

from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[3]
MANIFESTS_DIR = BASE_DIR / "docs" / "manifests"
REGISTRY_FILE = BASE_DIR / "docs" / "REGISTRY.md"


class ManifestLoader:
    """
    Loader de manifiestos ACTIVOS.
    La fuente de verdad es REGISTRY.md.
    """

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def _read_registry(self) -> List[str]:
        if not REGISTRY_FILE.exists():
            return []

        lines = REGISTRY_FILE.read_text(encoding="utf-8").splitlines()
        active = []

        inside_block = False
        for line in lines:
            line = line.strip()

            if line.startswith("```"):
                inside_block = not inside_block
                continue

            if inside_block and line.endswith(".md"):
                active.append(line)

        return active

    def load_all(self) -> Dict[str, str]:
        manifests: Dict[str, str] = {}

        for name in self._read_registry():
            path = MANIFESTS_DIR / name
            if path.exists():
                manifests[name] = path.read_text(encoding="utf-8")

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
