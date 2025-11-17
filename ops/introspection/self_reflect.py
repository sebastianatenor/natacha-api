"""
ops.introspection.self_reflect
---------------------------------
Módulo de auto-reflexión de Natacha.
Analiza introspecciones previas y genera sugerencias de mejora.
Guarda automáticamente los resultados como "pensamientos" en memory_store.jsonl.
"""

import json
from pathlib import Path
from fastapi import APIRouter
from collections import Counter
from datetime import datetime

router = APIRouter(prefix="/ops/introspection", tags=["Introspection"])


def load_introspection_history():
    """Carga introspecciones previas desde memory_store.jsonl."""
    path = Path("memory_store.jsonl")
    if not path.exists():
        return []
    data = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if '"introspection_result"' in line:
                try:
                    data.append(json.loads(line))
                except Exception:
                    continue
    return data


def save_reflection(reflection_text: str, summary: dict):
    """Guarda una reflexión generada en memory_store.jsonl."""
    path = Path("memory_store.jsonl")
    entry = {
        "timestamp": datetime.now().isoformat(),
        "kind": "self_reflection",
        "summary": summary,
        "thought": reflection_text,
    }
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"[OK] Reflexión guardada en {path}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar la reflexión: {e}")


@router.get("/reflect")
def reflect_on_self():
    """
    Analiza introspecciones previas y sugiere áreas de mejora.
    Además, guarda la reflexión en la memoria persistente.
    """
    history = load_introspection_history()
    if not history:
        return {"status": "error", "message": "No hay introspecciones previas."}

    all_issues = []
    for entry in history[-5:]:  # últimas 5 introspecciones
        issues = entry["detail"].get("issues", [])
        for i in issues:
            all_issues.append(i["file"])

    if not all_issues:
        return {"status": "ok", "message": "No se detectaron issues recientes 🎉"}

    counter = Counter(all_issues)
    most_common = counter.most_common(5)

    suggestions = [
        f"- Documentar funciones faltantes en `{file}` (ocurre {count} veces)"
        for file, count in most_common
    ]

    message = (
        "🧠 Auto-reflexión completada.\n\n"
        "Archivos más problemáticos:\n"
        + "\n".join(suggestions)
        + "\n\nSugerencia general: priorizar documentación y limpieza de código repetitivo."
    )

    # Guardar pensamiento en la memoria persistente
    save_reflection(message, {"issues_analyzed": len(all_issues), "files": most_common})

    return {
        "status": "ok",
        "issues_analyzed": len(all_issues),
        "common_files": most_common,
        "reflection": message,
        "saved": True,
    }
