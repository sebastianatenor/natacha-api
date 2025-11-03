import traceback
from datetime import datetime

from google.cloud import firestore


class NatachaMemory:
    """Memoria cognitiva de Natacha — registra, recuerda y aprende de la experiencia."""

    def __init__(self, project_id="asistente-sebastian"):
        self.project_id = project_id
        self.local_memory = []
        try:
            self.db = firestore.Client(project=project_id)
            self.online = True
            self._log_local(
                "Memory inicializada", "Conectada a Firestore", level="info"
            )
        except Exception as e:
            self.db = None
            self.online = False
            self._log_local("Error inicializando Memory", str(e), level="error")

    def _log_local(self, summary, detail, level="info"):
        """Guarda un registro local (memoria RAM)."""
        entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "level": level,
            "summary": summary,
            "detail": detail,
        }
        self.local_memory.append(entry)
        print(f"[MEMORY-{level.upper()}] {summary}: {detail}")

    def add_event(self, summary, detail, type="general", level="info"):
        """Agrega un evento a la memoria local y lo sincroniza con Firestore."""
        entry = {
            "timestamp": datetime.utcnow(),
            "summary": summary,
            "detail": detail,
            "level": level,
            "type": type,
        }

        self._log_local(summary, detail, level)

        if self.online:
            try:
                doc_ref = self.db.collection("natacha_memory").document()
                doc_ref.set(entry)
            except Exception as e:
                self._log_local("Error guardando en Firestore", str(e), level="warning")

    def recall_recent(self, limit=5):
        """Recupera los últimos eventos registrados."""
        if self.online:
            try:
                docs = (
                    self.db.collection("natacha_memory")
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .stream()
                )
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                self._log_local("Error leyendo memoria", str(e), level="error")
        return self.local_memory[-limit:]

    def analyze_patterns(self, limit=50):
        """Analiza los últimos registros en busca de patrones de error."""
        recent = self.recall_recent(limit)
        patterns = {"error": 0, "warning": 0, "info": 0}
        for entry in recent:
            lvl = entry.get("level", "info")
            if lvl in patterns:
                patterns[lvl] += 1
        total = sum(patterns.values())
        return {
            "patterns": patterns,
            "total": total,
            "analysis_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    def capture_exception(self, context, error):
        """Captura automáticamente una excepción con su traza completa."""
        trace = traceback.format_exc()
        self.add_event(
            f"Excepción en {context}",
            f"{error}\n\n{trace}",
            level="error",
            type="exception",
        )
