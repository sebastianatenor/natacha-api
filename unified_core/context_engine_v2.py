from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from unified_core.semantic_core import semantic_core


def safe_text(value):
    """Elimina caracteres Unicode inválidos."""
    if not isinstance(value, str):
        return value
    return value.encode("utf-8", "replace").decode("utf-8")


class ContextEngineV2:
    """
    Motor unificado de contexto v2 – versión estable y robusta.
    Incluye sanitización de Unicode para evitar Internal Server Error.
    """

    def __init__(self):
        self.system_rules: List[str] = [
            "You are Natacha, the assistant.",
            "Always maintain continuity and contextual awareness.",
            "Use semantic similarity to connect past and current topics.",
        ]

        self.memory_path = "memory_store.jsonl"

    def _load_recent_memory(self, limit: int = 20) -> List[Dict[str, Any]]:
        items = []
        try:
            with open(self.memory_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            # Sanitizar todos los campos string
                            clean = {}
                            for k, v in obj.items():
                                if isinstance(v, str):
                                    clean[k] = safe_text(v)
                                elif isinstance(v, list):
                                    clean[k] = [safe_text(x) for x in v]
                                else:
                                    clean[k] = v
                            items.append(clean)
                    except Exception:
                        continue
        except FileNotFoundError:
            return []

        # Ordenar si hay timestamps
        try:
            items = sorted(items, key=lambda x: x.get("timestamp", ""))
        except Exception:
            pass

        return items[-limit:] if limit else items

    def _semantic_pack(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for t in texts:
            try:
                vectors.append(semantic_core.embed(t))
            except Exception:
                vectors.append([])
        return vectors

    def _fallback_global(self) -> Dict[str, Any]:
        return {
            "type": "global_fallback",
            "content": [
                "Natacha is an AI assistant supporting Sebastián Atenor.",
                "Primary domains: logistics, AI agents, cloud infra, imports from China, LATAM markets.",
                "Maintain continuity, autonomy and reasoning depth.",
            ]
        }

    def _system_block(self) -> Dict[str, Any]:
        return {"type": "system", "content": self.system_rules}

    def _recent_block(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"type": "recent_messages", "count": len(items), "messages": items}

    def _semantic_block(self, texts: List[str], vectors: List[List[float]]) -> Dict[str, Any]:
        return {
            "type": "semantic_embeddings",
            "count": len(texts),
            "texts": texts,
            "vectors": vectors,
        }

    def build_context_bundle(self, user_id: Optional[str], recent_limit: int = 20, include_global_fallback: bool = True):
        recent_items = self._load_recent_memory(limit=recent_limit)

        semantic_texts = [safe_text(item.get("text", "")) for item in recent_items[-10:]]
        semantic_vectors = self._semantic_pack(semantic_texts)

        bundle = {
            "user_id": safe_text(user_id),
            "generated_at": datetime.utcnow().isoformat(),
            "recent_limit": recent_limit,
            "global_fallback": include_global_fallback,
            "context_blocks": [
                self._system_block(),
                self._recent_block(recent_items),
                self._semantic_block(semantic_texts, semantic_vectors),
            ]
        }

        if include_global_fallback and len(recent_items) < 3:
            bundle["context_blocks"].append(self._fallback_global())

        return bundle


context_engine_v2 = ContextEngineV2()


def build_context_bundle(user_id: Optional[str], recent_limit: int = 20, include_global_fallback: bool = True):
    return context_engine_v2.build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
        include_global_fallback=include_global_fallback,
    )
