# ops/system/perception_provider.py

from typing import Dict, Any
from datetime import datetime, timezone

def read_system_perception() -> Dict[str, Any]:
    """
    Fuente ÚNICA de percepción del sistema.
    Puede ser usada por:
    - routers HTTP
    - agent_interact
    - boot cognitivo
    """

    from routes.system_state.router import system_state

    # Reutilizamos estado real
    state_response = system_state()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **state_response["state"],
    }
