"""
ops.introspection.code_scan
---------------------------------
Motor inicial de introspección de código fuente.
Escanea archivos .py en el proyecto y detecta issues simples
(sintaxis, imports no usados, funciones sin docstring, etc.)
"""

import os
import ast
from fastapi import APIRouter

router = APIRouter(prefix="/ops/introspection", tags=["Introspection"])


def analyze_file(filepath: str):
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append({"file": filepath, "issue": f"SyntaxError: {e}"})
        return issues
    except Exception as e:
        issues.append({"file": filepath, "issue": f"ReadError: {e}"})
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not ast.get_docstring(node):
                issues.append({
                    "file": filepath,
                    "issue": f"Función '{node.name}' sin docstring"
                })
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "random":
                    issues.append({
                        "file": filepath,
                        "issue": "Importa 'random' (verificar si es necesario)"
                    })
    return issues


@router.post("/scan")
def scan_codebase():
    """Escanea el código fuente del proyecto."""
    import pathlib

    base_path = os.getcwd()
    results = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and "venv" not in root:
                filepath = os.path.join(root, file)
                results.extend(analyze_file(filepath))

    # Detectar versión actual
    rev_path = pathlib.Path(".rev")
    version = "v19.1-dev"
    if rev_path.exists():
        version = rev_path.read_text().strip()

    result = {
        "version": version,
        "files_scanned": len(results),
        "issues": results[:10],
        "status": "completed",
    }

    # Guardar resultado en memoria persistente
    try:
        from ops.introspection.memory_bridge import save_introspection_result
        save_introspection_result(result)
    except Exception as e:
        print(f"[WARN] Could not save result to memory: {e}")

    return result
