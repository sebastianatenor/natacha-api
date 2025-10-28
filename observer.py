from google.cloud import firestore
from datetime import datetime

db = firestore.Client()

def run_learning_cycle():
    print("🧠 Iniciando ciclo de aprendizaje...")
    plan_doc = db.collection("memories").document("plan_automatizacion").get()
    if not plan_doc.exists:
        print("❌ No hay plan maestro en memoria.")
        return
    data = plan_doc.to_dict()
    fases = [
        {"fase": "1", "nombre": "Consolidación base", "estado": "✅"},
        {"fase": "2", "nombre": "Supervisión inteligente", "estado": "🟡"},
        {"fase": "3", "nombre": "Autocuración", "estado": "⚪"},
        {"fase": "4", "nombre": "Comunicación autónoma", "estado": "⚪"},
        {"fase": "5", "nombre": "Gobernanza total", "estado": "⚪"},
    ]
    doc_id = f"progress_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    db.collection("progress_reports").document(doc_id).set({
        "timestamp": datetime.utcnow().isoformat(),
        "resultados": fases
    })
    print(f"✅ Progreso actualizado en Firestore ({doc_id})")

if __name__ == "__main__":
    run_learning_cycle()
