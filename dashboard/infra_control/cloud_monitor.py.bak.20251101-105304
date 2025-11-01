import streamlit as st
import subprocess
import pandas as pd
from datetime import datetime

def run_command(cmd):
    """Ejecuta comandos de gcloud y devuelve la salida limpia."""
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"⚠️ Error ejecutando: {cmd}\n{e.stderr.strip()}"

def show():
    st.title("☁️ Monitor de Infraestructura en la Nube (Google Cloud)")
    st.caption("Panel de estado de los servicios y recursos activos de Natacha")

    # --- Información general del proyecto
    st.subheader("📁 Proyecto actual")
    project_info = run_command("gcloud config get-value project")
    st.code(project_info if project_info else "Proyecto no configurado")

    # --- Cloud Run Services
    st.subheader("🚀 Servicios Cloud Run")
    services_output = run_command("gcloud run services list --platform managed --project asistente-sebastian --format=json")

    try:
        import json
        services = json.loads(services_output)
        if isinstance(services, list) and len(services) > 0:
            df_services = pd.DataFrame([{
                "Servicio": s["metadata"]["name"],
                "Región": s["location"],
                "URL": s["status"]["url"],
                "Última implementación": s["metadata"]["annotations"].get("serving.knative.dev/lastModifier", "N/A")
            } for s in services])
            st.dataframe(df_services, use_container_width=True)
        else:
            st.info("No se encontraron servicios Cloud Run activos.")
    except Exception:
        st.text(services_output)

    # --- Firestore
    st.subheader("🧠 Firestore (colecciones disponibles)")
    firestore_collections = run_command(
        "gcloud firestore collections list --project asistente-sebastian --format=value(name)"
    )
    if "ERROR" in firestore_collections or "INVALID_ARGUMENT" in firestore_collections:
        st.warning("Firestore no disponible o sin permisos.")
    elif firestore_collections.strip():
        cols = firestore_collections.splitlines()
        st.write(f"Se encontraron {len(cols)} colecciones:")
        st.code("\n".join(cols))
    else:
        st.info("No hay colecciones en Firestore o base vacía.")

    # --- Cloud Healthcare (FHIR)
    st.subheader("🏥 Cloud Healthcare (FHIR)")
    healthcare_datasets = run_command("gcloud healthcare datasets list --project asistente-sebastian --format=value(name)")
    if not healthcare_datasets.strip():
        st.info("No hay datasets FHIR disponibles o API no habilitada.")
    else:
        datasets = healthcare_datasets.splitlines()
        st.write(f"Datasets encontrados: {len(datasets)}")
        st.code("\n".join(datasets))
        for ds in datasets:
            stores = run_command(f"gcloud healthcare fhir-stores list --dataset={ds} --project asistente-sebastian --format=value(name)")
            if stores.strip():
                st.write(f"📦 FHIR Stores en `{ds}`:")
                st.code(stores)
            else:
                st.info(f"Sin FHIR Stores en dataset `{ds}`")

    # --- APIs habilitadas
    st.subheader("🔌 APIs habilitadas en el proyecto")
    apis_output = run_command("gcloud services list --enabled --project asistente-sebastian --format=value(config.name)")
    if apis_output.strip():
        apis = apis_output.splitlines()
        st.write(f"Total: {len(apis)} APIs habilitadas")
        st.code("\n".join(apis))
    else:
        st.info("No se pudieron listar las APIs habilitadas.")

    # --- Resumen
    st.divider()
    st.subheader("📊 Resumen de la Infraestructura Cloud")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cloud Run", len(services) if isinstance(services, list) else 0)
    col2.metric("Firestore", len(firestore_collections.splitlines()) if firestore_collections.strip() else 0)
    col3.metric("Datasets FHIR", len(healthcare_datasets.splitlines()) if healthcare_datasets.strip() else 0)
    col4.metric("APIs habilitadas", len(apis_output.splitlines()) if apis_output.strip() else 0)

    st.caption(f"Última actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
