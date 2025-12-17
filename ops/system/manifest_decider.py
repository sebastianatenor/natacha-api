# ops/system/manifest_decider.py

from dataclasses import dataclass
from typing import List, Dict


# ============================================================
# MODELS
# ============================================================

@dataclass
class SystemSuggestion:
    level: str              # info | warning | critical
    title: str
    message: str
    source_manifest: str


# ============================================================
# MANIFEST-DRIVEN DECIDER (PASIVO)
# ============================================================

class ManifestDecider:
    """
    Decisor cognitivo PASIVO.

    - Lee estado del sistema
    - Lee contexto reciente
    - Usa reglas de los manifiestos
    - Sugiere
    - NO ejecuta
    """

    def evaluate(
        self,
        system_state: Dict,
        recent_context: List[Dict],
        active_project: str | None = None
    ) -> List[SystemSuggestion]:

        suggestions: List[SystemSuggestion] = []

        # ----------------------------------------------------
        # 1. Sobrecarga cognitiva
        # ----------------------------------------------------
        if len(recent_context) > 30:
            suggestions.append(
                SystemSuggestion(
                    level="warning",
                    title="Sobrecarga cognitiva detectada",
                    message=(
                        "Demasiados eventos recientes activos. "
                        "Se recomienda pausar ejecución y priorizar."
                    ),
                    source_manifest="01_executive_priorities"
                )
            )

        # ----------------------------------------------------
        # 2. Memoria extensa
        # ----------------------------------------------------
        memory = system_state.get("memory", {})
        items = memory.get("items_count", 0)

        if items > 3000:
            suggestions.append(
                SystemSuggestion(
                    level="info",
                    title="Memoria extensa activa",
                    message=(
                        "La memoria supera un umbral alto. "
                        "Puede ser buen momento para consolidar aprendizajes."
                    ),
                    source_manifest="02_memory_manifest"
                )
            )

        # ----------------------------------------------------
        # 3. Proyecto activo sin foco
        # ----------------------------------------------------
        if active_project:
            found = any(
                active_project.lower() in (e.get("project") or "").lower()
                for e in recent_context
            )

            if not found:
                suggestions.append(
                    SystemSuggestion(
                        level="info",
                        title="Proyecto sin eventos recientes",
                        message=(
                            f"El proyecto '{active_project}' está activo "
                            "pero no aparece en el contexto reciente."
                        ),
                        source_manifest="04_project_model"
                    )
                )

        # ----------------------------------------------------
        # 4. Default
        # ----------------------------------------------------
        if not suggestions:
            suggestions.append(
                SystemSuggestion(
                    level="info",
                    title="Sistema estable",
                    message="No se detectan tensiones cognitivas.",
                    source_manifest="00_core_cognitive_manifest"
                )
            )

        return suggestions
