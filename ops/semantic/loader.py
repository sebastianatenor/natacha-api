import os
from ops.semantic.state import SEMANTIC_STATE


def init_semantic_engine():
    """
    Inicializa el motor semántico.
    NO rompe el arranque si falla.
    """
    hf_token = os.getenv("HF_TOKEN")

    SEMANTIC_STATE.hf_token_present = bool(hf_token)

    if not hf_token:
        SEMANTIC_STATE.loaded = False
        return

    # Placeholder hasta implementar modelo real
    SEMANTIC_STATE.model_name = "pending"
    SEMANTIC_STATE.loaded = False
