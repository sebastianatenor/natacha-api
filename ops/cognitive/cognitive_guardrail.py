# ops/cognitive/cognitive_guardrail.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from ops.cognitive.action_envelope import (
    ActionEnvelope,
    ActionEnvelopeBuilder,
    ActionType
)

# ============================================================
# ENUMS
# ============================================================

class MemoryLevel(str, Enum):
    NONE = "none"
    TEMPORARY = "temporary"
    EXECUTIVE = "executive"
    STRUCTURAL = "structural"


# ============================================================
# INPUT / OUTPUT MODELS
# ============================================================

@dataclass
class CognitiveInput:
    user_id: str
    message: str
    project: Optional[str] = None
    context: Optional[dict] = None


@dataclass
class CognitiveDecision:
    allow_response: bool
    store_memory: bool
    memory_level: MemoryLevel
    needs_clarification: bool
    warnings: List[str]

    # NUEVO
    proposed_action: Optional[ActionEnvelope] = None


# ============================================================
# GUARDRAIL CORE
# ============================================================

class CognitiveGuardrail:
    """
    Cognitive Guardrail
    -------------------
    Firewall cognitivo del agente.

    Decide:
    - si responde
    - si recuerda
    - qué nivel de memoria
    - si hay una acción potencial (NO ejecuta)
    """

    TRIVIAL_MESSAGES = {
        "ok", "dale", "si", "sí", "gracias", "hola", "listo"
    }

    def __init__(self):
        self.action_builder = ActionEnvelopeBuilder()

    def evaluate(self, payload: CognitiveInput) -> CognitiveDecision:
        msg = (payload.message or "").strip().lower()

        # ----------------------------
        # 1. Mensajes triviales
        # ----------------------------
        if msg in self.TRIVIAL_MESSAGES:
            return CognitiveDecision(
                allow_response=True,
                store_memory=False,
                memory_level=MemoryLevel.NONE,
                needs_clarification=False,
                warnings=[],
                proposed_action=None
            )

        # ----------------------------
        # 2. Sobrecarga / confusión
        # ----------------------------
        overload_signals = [
            "no sé por dónde",
            "estoy perdido",
            "tengo muchas cosas",
            "no llego",
            "todo junto",
            "no sé qué hacer"
        ]

        if any(s in msg for s in overload_signals):
            return CognitiveDecision(
                allow_response=True,
                store_memory=True,
                memory_level=MemoryLevel.EXECUTIVE,
                needs_clarification=True,
                warnings=[],
                proposed_action=None
            )

        # ----------------------------
        # 3. Estrategia / decisiones
        # ----------------------------
        strategic_keywords = [
            "prioridad",
            "decidir",
            "estrategia",
            "qué conviene",
            "próximo paso",
            "plan"
        ]

        if any(k in msg for k in strategic_keywords):
            return CognitiveDecision(
                allow_response=True,
                store_memory=True,
                memory_level=MemoryLevel.STRUCTURAL,
                needs_clarification=False,
                warnings=[],
                proposed_action=None
            )

        # ----------------------------
        # 4. Intención de acción (PROPOSAL ONLY)
        # ----------------------------
        action = self.action_builder.build(payload.message)

        if action.action_type != ActionType.UNKNOWN:
            return CognitiveDecision(
                allow_response=True,
                store_memory=False,
                memory_level=MemoryLevel.NONE,
                needs_clarification=True,
                warnings=["ACTION_PROPOSED_NOT_EXECUTED"],
                proposed_action=action
            )

        # ----------------------------
        # 5. Default seguro
        # ----------------------------
        return CognitiveDecision(
            allow_response=True,
            store_memory=True,
            memory_level=MemoryLevel.TEMPORARY,
            needs_clarification=False,
            warnings=[],
            proposed_action=None
        )
