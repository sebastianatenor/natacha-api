import datetime

from google.cloud import firestore


def cargar_plan_automatizacion():
    db = firestore.Client()
    doc = db.collection("memories").document("plan_automatizacion").get()
    if doc.exists:
        plan = doc.to_dict()
        print("📋 Plan maestro cargado:", plan["summary"])
        return plan
    else:
        print("⚠️ No se encontró el plan maestro en Firestore.")
        return None


def evaluar_progreso(plan):
    if not plan:
        return []

    contenido = plan["detail"]
    resultados = []
    fases = {
        "Fase 1": "Consolidación base",
        "Fase 2": "Supervisión inteligente",
        "Fase 3": "Autocuración",
        "Fase 4": "Comunicación autónoma",
        "Fase 5": "Gobernanza total y autonomía",
    }

    print("\n📊 Evaluación automática del plan de automatización:\n")
    for fase, nombre in fases.items():
        if nombre in contenido:
            start = contenido.find(nombre)
            snippet = contenido[start : start + 200].split("\n")[0]
            progreso = "✅" if "✅" in snippet else "🟡" if "🟡" in snippet else "⚪"
            resultados.append(
                {
                    "fase": fase,
                    "nombre": nombre,
                    "estado": progreso,
                    "extracto": snippet.strip(),
                }
            )
            print(f" - {fase} ({nombre}): {progreso}")
        else:
            print(f" - {fase}: no encontrada en el texto.")

    print("\n✅ Evaluación completada.\n")
    return resultados


def registrar_progreso(resultados):
    if not resultados:
        print("⚠️ No hay resultados para registrar.")
        return

    db = firestore.Client()
    doc_id = f"progress_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    db.collection("progress_reports").document(doc_id).set(
        {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "resultados": resultados,
            "source": "observer.py",
            "type": "Autoevaluación de plan",
        }
    )
    print(f"🧠 Reporte guardado en Firestore: progress_reports/{doc_id}")


def run_learning_cycle():
    print("🤖 Iniciando ciclo de aprendizaje supervisado...")
    plan = cargar_plan_automatizacion()
    resultados = evaluar_progreso(plan)
    registrar_progreso(resultados)
    print("🔁 Ciclo completado.\n")


if __name__ == "__main__":
    run_learning_cycle()
