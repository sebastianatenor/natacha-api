from pathlib import Path

SKIP_DIR_NAMES = {'.venv', '__pycache__', 'logs', 'backups', '.git'}

def should_skip(path: str) -> bool:
    parts = Path(path).parts
    # saltar directorios ruidosos
    if any(p in SKIP_DIR_NAMES for p in parts):
        return True
    # saltar dist-info de paquetes instalados
    if any(seg.endswith('.dist-info') for seg in parts):
        return True
    # saltar bytecode
    if path.endswith('.pyc'):
        return True
    return False
