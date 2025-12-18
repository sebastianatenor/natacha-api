# ops/memory/manager.py
from typing import Dict
from threading import Lock

from ops.memory.user_context import UserCognitiveState


class UserContextManager:
    """
    Gestor de estados cognitivos vivos.
    Vive en RAM.
    Se reinicia si el contenedor cae (aceptable).
    """

    def __init__(self):
        self._store: Dict[str, UserCognitiveState] = {}
        self._lock = Lock()

    def get(self, user_id: str) -> UserCognitiveState:
        with self._lock:
            if user_id not in self._store:
                self._store[user_id] = UserCognitiveState(user_id=user_id)
            return self._store[user_id]

    def touch(self, user_id: str, channel: str = "unknown") -> UserCognitiveState:
        state = self.get(user_id)
        state.touch(channel=channel)
        return state

    def mark_escalation(self, user_id: str):
        state = self.get(user_id)
        state.mark_escalation()
        return state

    def add_pending(self, user_id: str, note: str):
        state = self.get(user_id)
        state.add_pending(note)
        return state

    def snapshot(self, user_id: str) -> dict:
        """
        Devuelve una vista serializable del estado vivo.
        """
        state = self.get(user_id)
        return {
            "user_id": state.user_id,
            "last_seen": state.last_seen.isoformat(),
            "channel": state.channel,
            "emotional_tone": state.emotional_tone,
            "confidence_level": state.confidence_level,
            "current_topic": state.current_topic,
            "stage": state.stage,
            "pending_items": list(state.pending_items),
            "escalation_required": state.escalation_required,
        }


# Singleton canónico
user_context_manager = UserContextManager()
