# ops/memory/user_context.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class UserCognitiveState:
    """
    Estado cognitivo VIVO por usuario.
    NO es memoria histórica.
    NO es vectorial.
    Es mutable, temporal y contextual.
    """

    user_id: str

    # Meta
    last_seen: datetime = field(default_factory=datetime.utcnow)
    channel: str = "unknown"

    # Estado cognitivo
    emotional_tone: str = "neutral"      # neutral | focused | confused | frustrated | positive
    confidence_level: str = "unknown"    # low | medium | high | unknown

    # Contexto operativo
    current_topic: Optional[str] = None
    stage: Optional[str] = None           # inquiry | evaluation | negotiation | execution

    # Continuidad
    pending_items: List[str] = field(default_factory=list)
    escalation_required: bool = False

    def touch(self, channel: Optional[str] = None):
        """Actualiza presencia del usuario."""
        self.last_seen = datetime.utcnow()
        if channel:
            self.channel = channel

    def mark_escalation(self):
        self.escalation_required = True

    def add_pending(self, note: str):
        if note not in self.pending_items:
            self.pending_items.append(note)
