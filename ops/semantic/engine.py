from ops.semantic.schema import SemanticAnalysis, SemanticSignal
from ops.semantic.state import SEMANTIC_STATE


class SemanticEngine:
    """
    Motor semántico central.
    """

    def analyze(self, text: str) -> SemanticAnalysis:
        """
        Analiza texto SIEMPRE.
        Nunca ejecuta acciones.
        Nunca rompe.
        """

        if not SEMANTIC_STATE.loaded:
            signals = SemanticSignal(
                intent="unknown",
                risk_level="unknown",
                domains=[],
                confidence=0.0,
            )

            return SemanticAnalysis(
                text=text,
                signals=signals,
                model_used=None,
            )

        raise NotImplementedError("Semantic engine not implemented yet")


semantic_engine = SemanticEngine()
