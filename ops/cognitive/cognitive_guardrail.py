# ops/cognitive/cognitive_guardrail.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


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


# ============================================================
# GUARDRAIL CORE
# ============================================================

from ops.cognitive.project_profiles import PROJECT_PROFILES

class CognitiveGuardrail:
    """
    Cognitive Guardrail
    -------------------
    Este módulo define:
    - Qué se responde
    - Qué se recuerda
    - Qué NO se ejecuta
    - Qué requiere aclaración

    Es el firewall cognitivo del agente.
    """

    TRIVIAL_MESSAGES = {
        "ok", "dale", "si", "sí", "gracias", "hola", "listo"
    }

    def evaluate(self, payload: CognitiveInput) -> CognitiveDecision:
        msg = (payload.message or "").strip().lower()

        # ----------------------------
        # 0. Project cognitive profile
        # ----------------------------
        profile = None
        if payload.project:
            profile = PROJECT_PROFILES.get(payload.project.upper())

        if profile:
            # Ajustes futuros: tono, foco, sesgo de memoria
            pass

        # ----------------------------
        # 1. Mensajes triviales
        # ----------------------------
        if msg in self.TRIVIAL_MESSAGES:
            return CognitiveDecision(
                allow_response=True,
                store_memory=False,
                memory_level=MemoryLevel.NONE,
                needs_clarification=False,
                warnings=[]
            )

        # ----------------------------
        # 2. Señales de sobrecarga / confusión
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
                warnings=[]
            )

        # ----------------------------
        # 3. Decisiones / estrategia / prioridades
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
                warnings=[]
            )

        # ----------------------------
        # 4. Acciones explícitas (NO ejecutar)
        # ----------------------------
        action_verbs = [
            "mandá",
            "enviá",
            "borrá",
            "creá",
            "eliminá",
            "ejecutá"
        ]

        if any(v in msg for v in action_verbs):
            return CognitiveDecision(
                allow_response=True,
                store_memory=False,
                memory_level=MemoryLevel.NONE,
                needs_clarification=True,
                warnings=["ACTION_REQUEST_REQUIRES_PERMISSION"]
            )

        # ----------------------------
        # 5. Default seguro
        # ----------------------------
        return CognitiveDecision(
            allow_response=True,
            store_memory=True,
            memory_level=MemoryLevel.TEMPORARY,
            needs_clarification=False,
            warnings=[]
        )
