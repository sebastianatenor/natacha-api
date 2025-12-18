from typing import Optional


class SemanticState:
    """
    Estado runtime del motor semántico
    """
    loaded: bool = False
    model_name: Optional[str] = None
    embedding_dim: Optional[int] = None
    hf_token_present: bool = False


SEMANTIC_STATE = SemanticState()
