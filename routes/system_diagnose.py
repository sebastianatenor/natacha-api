from fastapi import APIRouter
from typing import Dict, Any
import traceback

from routes.system_state import system_state
from ops.system_interpreter import interpret_system_state

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/diagnose")
def system_diagnose() -> Dict[str, Any]:
    """
    Diagnóstico del sistema.
    ⚠️ Este endpoint NUNCA debe romper ni devolver 500.
    Siempre responde JSON, incluso ante errores internos.
    """

    try:
        raw_state = system_state()

        try:
            diagnosis = interpret_system_state(raw_state)
        except Exception as e:
            # Error lógico de interpretación (lazy memory, semantic aún no listo, etc.)
            return {
                "state": raw_state,
                "diagnosis": {
                    "status": "degraded",
                    "issues": [],
                    "warnings": [
                        "Diagnosis interpreter failed"
                    ],
                    "error": str(e),
                    "summary": {
                        "semantic_loaded": raw_state.get("semantic", {}).get("loaded"),
                        "memory_present": raw_state.get("memory", {}).get("store_available"),
                        "cloud_run": raw_state.get("runtime", {}).get("cloud_run"),
                    },
                },
            }

        return {
            "state": raw_state,
            "diagnosis": diagnosis,
        }

    except Exception as e:
        # Error CRÍTICO e inesperado → igual respondemos JSON
        return {
            "state": None,
            "diagnosis": {
                "status": "error",
                "issues": ["system_diagnose_crash"],
                "warnings": [],
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        }
