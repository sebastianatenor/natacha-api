# ops/cognitive/memory_manifest.py

"""
MEMORY MANIFEST — Natacha Cognitive Core
---------------------------------------

Este manifiesto define:
- Qué tipo de información se guarda
- En qué nivel de memoria
- Qué se compacta
- Qué se descarta

Objetivo:
Escalabilidad cognitiva sin saturación.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List


class MemoryLevel(str, Enum):
    NONE = "none"
    TEMPORARY = "temporary"
    EXECUTIVE = "executive"
    STRUCTURAL = "structural"


@dataclass
class MemoryRule:
    name: str
    description: str
    memory_level: MemoryLevel
    ttl_days: int
    compactable: bool


# ============================================================
# MEMORY RULESET
# ============================================================

MEMORY_RULES: List[MemoryRule] = [

    MemoryRule(
        name="trivial_conversation",
        description="Saludos, confirmaciones, frases sin valor decisional",
        memory_level=MemoryLevel.NONE,
        ttl_days=0,
        compactable=False,
    ),

    MemoryRule(
        name="working_context",
        description="Contexto operativo reciente, seguimiento corto",
        memory_level=MemoryLevel.TEMPORARY,
        ttl_days=14,
        compactable=True,
    ),

    MemoryRule(
        name="executive_decisions",
        description="Decisiones, prioridades, bloqueos, compromisos",
        memory_level=MemoryLevel.EXECUTIVE,
        ttl_days=180,
        compactable=True,
    ),

    MemoryRule(
        name="structural_knowledge",
        description="Estrategia, reglas, aprendizajes, modelos mentales",
        memory_level=MemoryLevel.STRUCTURAL,
        ttl_days=365,
        compactable=False,
    ),
]
