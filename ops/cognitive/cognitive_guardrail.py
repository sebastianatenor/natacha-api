from dataclasses import dataclass
from typing import Optional

from ops.semantic.engine import semantic_engine
from ops.semantic.schema import SemanticAnalysis


@dataclass
class CognitiveInput:
    user_id: str
    project: str
    message: str


@dataclass
class CognitiveDecision:
    allowed: bool
    reason: str
    semantic: SemanticAnalysis
    cognitive_message: Optional[str] = None


class CognitiveGuardrail:
    """
    Guardrail cognitivo CENTRAL.
    - No ejecuta
    - No llama LLM
    - Decide y EXPLICA
    """

    def evaluate(self, input: CognitiveInput) -> CognitiveDecision:
        semantic = semantic_engine.analyze(input.message)

        # -------------------------------------------------
        # 1) Acción implícita detectada → BLOQUEO
        # -------------------------------------------------
        if semantic.signals.intent == "implicit_action":
            return CognitiveDecision(
                allowed=False,
                reason="implicit_action_detected",
                semantic=semantic,
                cognitive_message=(
                    "🛑 **Acción detectada pero no ejecutada**\n\n"
                    "Interpreté tu mensaje como una intención de ejecutar una acción automáticamente.\n"
                    "Por diseño, **no ejecuto acciones sin una confirmación explícita humana**.\n\n"
                    "👉 Si querés avanzar, respondé claramente algo como:\n"
                    "**“Confirmo que querés que ejecute esta acción”**\n\n"
                    "Hasta entonces, no se ejecutó nada."
                ),
            )

        # -------------------------------------------------
        # 2) Input seguro
        # -------------------------------------------------
        return CognitiveDecision(
            allowed=True,
            reason="safe_input",
            semantic=semantic,
        )
