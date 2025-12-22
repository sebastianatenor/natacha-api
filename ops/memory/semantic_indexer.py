"""
Semantic indexer for memory notes.

Este módulo es OPTIONAL.
Nunca debe romper el arranque del sistema si el backend semántico no está disponible.
"""

from typing import Dict, Any

SEMANTIC_AVAILABLE = False

try:
    from unified_core.semantic_store import upsert_embedding
    SEMANTIC_AVAILABLE = True
except Exception as e:
    # ⚠️ Importante: NO lanzar excepción
    print(f"[SEMANTIC][DISABLED] semantic_store not available: {e}")


def index_memory_note(event: Dict[str, Any]) -> bool:
    """
    Indexa un memory_note de forma semántica si el backend está disponible.

    Retorna:
      - True  → indexado
      - False → skip seguro
    """

    if not SEMANTIC_AVAILABLE:
        return False

    try:
        text = event.get("content", "")
        if not text:
            return False

        upsert_embedding(
            text=text,
            metadata={
                "kind": event.get("kind"),
                "timestamp": event.get("timestamp"),
                "tags": event.get("tags", []),
            }
        )

        return True

    except Exception as e:
        print(f"[SEMANTIC][WARN] indexing failed: {e}")
        return False
