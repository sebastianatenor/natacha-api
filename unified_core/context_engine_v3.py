from unified_core.sanitize import sanitize
from datetime import datetime
from typing import List, Dict, Any, Optional

from unified_core.semantic_core import semantic_core


class ContextEngineV3:
    """
    Context Engine V3 – versión profesional.
    Combina:
      - recent memory
      - relevance scoring
      - semantic embeddings
      - structured blocks
      - system rules
      - global fallback (opcional)
    """

    def __init__(self):
        self.system_rules: List[str] = [
            "Your name is Natacha, assistant to Sebastián Atenor.",
            "Maintain long-term continuity, context integrity and reasoning depth.",
            "Prioritize business domains: imports, logistics, China suppliers, AI infra, LATAM industries.",
            "Use semantic similarity and relevance scoring to select what truly matters.",
        ]

        self.memory_path = "memory_store.jsonl"

    # -------------------------------------------------------
    # 1) Load recent memory
    # -------------------------------------------------------
    def _load_recent_memory(self, limit: int = 30) -> List[Dict[str, Any]]:
        items = []

        try:
            with open(self.memory_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = eval(line)
                        if isinstance(obj, dict):
                            items.append(obj)
                    except:
                        continue
        except FileNotFoundError:
       	    return []

        # Sort by timestamp if available
        try:
            items = sorted(items, key=lambda x: x.get("timestamp", ""))
        except:
            pass

        return items[-limit:]

    # -------------------------------------------------------
    # 2) Relevance scoring
    # -------------------------------------------------------
    def _score(self, item: Dict[str, Any]) -> float:
        text = item.get("text", "")
        score = 0.0

        if not text:
            return 0

        # Clients with priority
        priority_clients = ["Nubicom", "Aguas del Norte", "Reinaldo Atenor"]
        for c in priority_clients:
            if c.lower() in text.lower():
                score += 5

        # Imports & logistics topics
        keywords = ["excavator", "forklift", "VIN", "China", "import", "logistics"]
        for k in keywords:
            if k.lower() in text.lower():
                score += 3

        # General relevance boost
        score += len(text) / 200

        return score

    # -------------------------------------------------------
    # 3) Select top messages
    # -------------------------------------------------------
    def _select_relevant(self, items: List[Dict[str, Any]], k: int = 10) -> List[Dict[str, Any]]:
        scored = [(self._score(item), item) for item in items]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:k]]

    # -------------------------------------------------------
    # 4) Semantic embeddings
    # -------------------------------------------------------
    def _semantic_pack(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for t in texts:
            try:
                vectors.append(semantic_core.embed(t))
            except:
                vectors.append([])
        return vectors

    # -------------------------------------------------------
    # 5) Fallback global
    # -------------------------------------------------------
    def _fallback_global(self) -> Dict[str, Any]:
        return {
            "type": "global_fallback",
            "content": [
                "Natacha serves Sebastián Atenor.",
                "She must maintain continuity, memory, reasoning and task integrity.",
                "Primary domains: imports, China, logistics, suppliers, LATAM industries, AI infra.",
            ]
        }

    # -------------------------------------------------------
    # 6) System block
    # -------------------------------------------------------
    def _system_block(self):
        return {"type": "system", "content": self.system_rules}

    # -------------------------------------------------------
    # 7) Build the final context bundle
    # -------------------------------------------------------
    def build(self, user_id: Optional[str], limit: int = 30, fallback: bool = True):
        items = self._load_recent_memory(limit)
        selected = self._select_relevant(items)

        semantic_texts = [i.get("text", "") for i in selected]
        semantic_vectors = self._semantic_pack(semantic_texts)

        bundle = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "recent_items": len(items),
            "selected_items": selected,
            "context_blocks": [
                self._system_block(),
                {"type": "relevant_messages", "messages": selected},
                {"type": "semantic_embeddings", "texts": semantic_texts, "vectors": semantic_vectors},
            ],
        }

        if fallback and len(selected) < 3:
            bundle["context_blocks"].append(self._fallback_global())

        return sanitize(bundle)


# Singleton instance
context_engine_v3 = ContextEngineV3()


# Public API-level function
def build_context_bundle(user_id: Optional[str], recent_limit: int = 30, include_global_fallback: bool = True):
    return context_engine_v3.build(
        user_id=user_id,
        limit=recent_limit,
        fallback=include_global_fallback,
    )

