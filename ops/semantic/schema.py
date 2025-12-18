from pydantic import BaseModel
from typing import List, Optional


class SemanticSignal(BaseModel):
    """
    Resultado SEMÁNTICO PURO.
    No decide nada. No ejecuta nada.
    """
    intent: str
    risk_level: str
    domains: List[str]
    confidence: float


class SemanticAnalysis(BaseModel):
    """
    Output completo del motor semántico
    """
    text: str
    signals: SemanticSignal
    model_used: Optional[str] = None
    embedding_dim: Optional[int] = None
