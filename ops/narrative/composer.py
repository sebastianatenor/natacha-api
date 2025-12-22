# ops/narrative/composer.py

from typing import Dict, Any


def compose_system_narrative(perceived_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye una narrativa humana y controlada
    a partir de percepción REAL del sistema.

    ❌ No infiere
    ❌ No evalúa
    ❌ No exagera
    ✅ Solo describe hechos observados
    """

    if not perceived_state:
        return {
            "summary": "Estado perceptivo no disponible",
            "confidence": "low",
        }

    memory = perceived_state.get("memory", {})
    semantic = perceived_state.get("semantic", {})
    timeline = perceived_state.get("timeline", {})

    summary_lines = []

    # Servicio
    service = perceived_state.get("service")
    revision = perceived_state.get("revision")
    if service:
        summary_lines.append(f"Servicio activo: {service}")
    if revision:
        summary_lines.append(f"Revisión en ejecución: {revision}")

    # Memoria
    if memory.get("exists"):
        summary_lines.append("Memoria canónica activa")
    else:
        summary_lines.append("Memoria canónica no detectada")

    # Semántica
    if semantic.get("loaded"):
        summary_lines.append("Motor semántico cargado")
    else:
        summary_lines.append("Motor semántico disponible bajo demanda")

    # Timeline
    events_total = timeline.get("events_total")
    if isinstance(events_total, int):
        summary_lines.append(f"Eventos cognitivos registrados: {events_total}")

    return {
        "summary": ". ".join(summary_lines),
        "raw_state": {
            "service": service,
            "revision": revision,
            "memory_active": bool(memory.get("exists")),
            "semantic_loaded": bool(semantic.get("loaded")),
            "events_total": events_total,
        },
        "confidence": "high",
    }
