# ops/cognitive/manifest_memory_binding.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict


# ============================================================
# ENUMS
# ============================================================

class MemoryScope(str, Enum):
    NONE = "none"
    TEMPORARY = "temporary"
    EXECUTIVE = "executive"
    STRUCTURAL = "structural"


# ============================================================
# MODELS
# ============================================================

@dataclass
class MemoryDecision:
    store: bool
    scope: MemoryScope
    reason: str
    source_manifest: str


# ============================================================
# MANIFEST → MEMORY RULES
# ============================================================

class ManifestMemoryPolicy:
    """
    Traduce manifiestos cognitivos en decisiones de memoria.

    NO escribe memoria.
    NO toca storage.
    SOLO define intención.
    """

    def decide(
        self,
        message: str,
        project: str,
        manifest_context: Dict
    ) -> MemoryDecision:

        msg = (message or "").lower()

        # ----------------------------
        # Trivial / conversacional
        # ----------------------------
        if msg in {"ok", "dale", "gracias", "sí", "si", "listo"}:
            return MemoryDecision(
                store=False,
                scope=MemoryScope.NONE,
                reason="trivial_message",
                source_manifest="02_memory_manifest"
            )

        # ----------------------------
        # Estrategia / decisión
        # ----------------------------
        strategy_keywords = [
            "prioridad",
            "decisión",
            "estrategia",
            "qué conviene",
            "plan",
            "siguiente paso"
        ]

        if any(k in msg for k in strategy_keywords):
            return MemoryDecision(
                store=True,
                scope=MemoryScope.STRUCTURAL,
                reason="strategic_decision",
                source_manifest="01_executive_priorities"
            )

        # ----------------------------
        # Operativo / seguimiento
        # ----------------------------
        operational_keywords = [
            "reunión",
            "cliente",
            "proveedor",
            "importación",
            "cotización",
            "tarea"
        ]

        if any(k in msg for k in operational_keywords):
            return MemoryDecision(
                store=True,
                scope=MemoryScope.EXECUTIVE,
                reason="operational_context",
                source_manifest="02_memory_manifest"
            )

        # ----------------------------
        # Default seguro
        # ----------------------------
        return MemoryDecision(
            store=True,
            scope=MemoryScope.TEMPORARY,
            reason="default_context",
            source_manifest="02_memory_manifest"
        )
