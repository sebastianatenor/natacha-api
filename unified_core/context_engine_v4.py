from datetime import datetime
from typing import Dict, Any, List

from unified_core.memory_lazy import get_memory_index
from unified_core.vectorstore.store import vector_store


class ContextEngineV4:
    def __init__(self):
        self.system_rules = [
            "Your name is Natacha, assistant to Sebastián Atenor.",
            "Maintain long-term continuity and recover previous context even across restarts.",
            "Prioritize reasoning quality, memory coherence and task autonomy.",
            "Domains: China suppliers, imports, logistics, LATAM industry intelligence, AI infra.",
            "Use semantic relevance AND topic relevance to choose the right memory.",
        ]

    def _system_block(self):
        return {"type": "system", "content": self.system_rules}

    def _fallback_block(self):
        return {
            "type": "fallback",
            "content": [
                "Natacha is stable even when memory is minimal.",
                "Primary mission: support Sebastián in operations, logistics, China suppliers and automation.",
            ]
        }

    def _recent_block(self, recent):
        return {"type": "recent_messages", "count": len(recent), "messages": recent}

    def _semantic_block(self, sem):
        texts = [x["text"] for x in sem]
        return {"type": "semantic_relevance", "count": len(texts), "texts": texts}

    def _select_semantic(self, query: str, k: int = 5):
        try:
            return vector_store.search(query, top_k=k)
        except Exception:
            return []

    def _select_priority_items(self, recent):
        priority = []
        for item in recent:
            tags = item.get("tags", [])
            if any(t in tags for t in ["lead", "client", "logistics", "import", "project"]):
                priority.append(item)
        return priority[-5:]

    def build_context_bundle(
        self,
        user_id: str,
        limit: int = 20,
        fallback: bool = True,
        query: str = "",
    ):
        memory = get_memory_index()

        # 🔑 ESTA ES LA CLAVE
        recent = memory.list_recent(limit=limit)

        semantic_hits = self._select_semantic(query, k=5) if query else []
        priority = self._select_priority_items(recent)

        blocks = [
            self._system_block(),
            self._recent_block(recent),
        ]

        if semantic_hits:
            blocks.append(self._semantic_block(semantic_hits))

        if priority:
            blocks.append({"type": "priority_context", "messages": priority})

        if fallback and len(recent) < 3:
            blocks.append(self._fallback_block())

        return {
            "status": "ok",
            "engine": "v4",
            "generated_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "recent_items": len(recent),
            "priority_items": len(priority),
            "semantic_items": len(semantic_hits),
            "memory_loaded": memory.store_loaded,
            "context_blocks": blocks,
        }


context_engine_v4 = ContextEngineV4()


def build_context_bundle(user_id: str, limit: int = 20, fallback: bool = True, query: str = ""):
    return context_engine_v4.build_context_bundle(
        user_id=user_id,
        limit=limit,
        fallback=fallback,
        query=query,
    )
