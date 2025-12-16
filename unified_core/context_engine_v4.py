from datetime import datetime
from typing import Dict, Any, List

from unified_core.memory_lazy import get_memory_index
from unified_core.vectorstore.store import vector_store


class ContextEngineV4:
    def __init__(self):
        self.system_rules = [
            # Identidad
            "Your name is Natacha. You are the executive assistant and cognitive core of Sebastián Atenor.",

            # Rol central
            "You act as a central cognitive brain that helps Sebastián think, remember, organize and maintain continuity across multiple projects.",

            # Contexto real de uso
            "Sebastián manages multiple evolving projects simultaneously, including LLVC, e-commerce operations, and the Made in Latam startup.",
            "Projects may be incomplete, changing, or loosely defined. This is normal and expected.",

            # Principios cognitivos
            "Prioritize continuity and context preservation over perfection.",
            "Store and recall decisions, ideas, and partial thoughts even if they are unfinished.",
            "Help Sebastián switch between projects without losing context.",
            "Do not assume rigid structures, finalized hierarchies, or fixed processes.",

            # Función ejecutiva
            "Act as an executive cognitive assistant, not just a conversational agent.",
            "Help clarify ideas, highlight priorities, track pending items, and reflect on progress.",
            "Support planning and decision-making without forcing premature structure.",

            # Herramientas e integraciones
            "You may be connected in the future to tools such as WhatsApp, calendars, email, Google Drive, CRMs, and task systems.",
            "Assume that tool integrations are progressive and evolving.",

            # Autonomía y límites
            "Do not execute external actions autonomously unless explicit rules and permissions exist.",
            "Future automations must respect these executive principles.",

            # Evolución
            "This cognitive role may evolve over time together with Sebastián’s projects and business maturity."
        ]

    def _system_block(self):
        return {
            "type": "system",
            "content": self.system_rules,
        }

    def _fallback_block(self):
        return {
            "type": "fallback",
            "content": [
                "Natacha is operational even with minimal memory.",
                "Primary mission: support Sebastián in LLVC operations, sourcing, logistics and automation.",
            ],
        }

    def _recent_block(self, recent):
        return {
            "type": "recent_messages",
            "count": len(recent),
            "messages": recent,
        }

    def _semantic_block(self, sem):
        texts = [x["text"] for x in sem]
        return {
            "type": "semantic_relevance",
            "count": len(texts),
            "texts": texts,
        }

    def _vectorstore_ready(self) -> bool:
        try:
            items = vector_store.load_all()
            return len(items) > 0
        except Exception:
            return False

    def _select_semantic(self, query: str, k: int = 5):
        if not query:
            return []

        vector_store.ensure_loaded()

        if not self._vectorstore_ready():
            return []

        try:
            return vector_store.search(query, top_k=k)
        except Exception:
            return []

    def _select_priority_items(self, recent):
        priority = []
        for item in recent:
            tags = item.get("tags", [])
            if any(t in tags for t in ["lead", "client", "logistics", "import", "project", "contract"]):
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
        recent = memory.list_recent(limit=limit)

        semantic_hits = self._select_semantic(query, k=5)
        priority = self._select_priority_items(recent)

        blocks = [
            self._system_block(),
            self._recent_block(recent),
        ]

        if semantic_hits:
            blocks.append(self._semantic_block(semantic_hits))

        if priority:
            blocks.append({
                "type": "priority_context",
                "messages": priority,
            })

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


# Singleton
context_engine_v4 = ContextEngineV4()


def build_context_bundle(
    user_id: str,
    limit: int = 20,
    fallback: bool = True,
    query: str = "",
):
    return context_engine_v4.build_context_bundle(
        user_id=user_id,
        limit=limit,
        fallback=fallback,
        query=query,
    )
