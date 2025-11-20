# 🧩 local_firestore_mock.py
# Mock mínimo para reemplazar Firestore en entorno local.
# No guarda nada en disco, solo imprime las llamadas para debug.

class LocalFirestoreMock:
    def collection(self, name):
        print(f"[MOCK Firestore] Accediendo a colección: {name}")
        return self

    def add(self, data):
        print(f"[MOCK Firestore] Agregando documento: {data}")
        return ("mock-id", None)

    def stream(self):
        print("[MOCK Firestore] Stream vacío")
        return []

    def document(self, name=None):
        print(f"[MOCK Firestore] Documento solicitado: {name}")
        return self

    def set(self, data):
        print(f"[MOCK Firestore] Set de documento: {data}")
        return None

    def get(self):
        print("[MOCK Firestore] Get vacío (sin datos)")
        return None
