import json
import subprocess
from datetime import datetime

import docker
import pandas as pd
import streamlit as st
from google.cloud import firestore

# =====================================================
# 🌐 PANEL DE INFRAESTRUCTURA UNIFICADA DE NATACHA
# =====================================================

st.set_page_config(page_title="Infraestructura Natacha", layout="wide", page_icon="🧭")

st.title("🧭 Infraestructura del Sistema Natacha")
st.caption(
    "Panel unificado de control de servicios locales (Docker) y en la nube (Cloud Run, Firestore, FHIR)"
)

st.divider()

# =====================================================
# 🕒 Encabezado general
# =====================================================
now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
st.sidebar.markdown(f"🕒 **Última actualización:** {now}")
st.sidebar.markdown("🔄 Recarga manual con `R` o actualiza cada 1 min")

# =====================================================
# 🔹 TABS
# =====================================================
tab_resumen, tab_docker, tab_cloudrun, tab_firestore, tab_fhir = st.tabs(
    ["📊 Resumen General", "🐳 Docker Local", "☁️ Cloud Run", "🔥 Firestore", "🧬 FHIR"]
)

# =====================================================
# 📊 TAB 1 - RESUMEN GENERAL
# =====================================================
with tab_resumen:
    st.header("📊 Estado General del Sistema")

    col1, col2, col3, col4 = st.columns(4)

    # Docker Summary
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        total_docker = len(containers)
        activos = len([c for c in containers if c.status == "running"])
        col1.metric(
            "🐳 Contenedores Docker",
            f"{activos}/{total_docker}",
            delta=f"{total_docker - activos} detenidos",
        )
    except:
        col1.error("Docker no disponible")

    # Cloud Run Summary
    try:
        cmd = [
            "gcloud",
            "run",
            "services",
            "list",
            "--platform",
            "managed",
            "--project",
            "asistente-sebastian",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        services = json.loads(result.stdout)
        activos = len(services)
        col2.metric("☁️ Servicios Cloud Run", activos)
    except:
        col2.error("Error con Cloud Run")

    # Firestore Summary
    try:
        db = firestore.Client()
        col3.metric("🔥 Firestore", "Conectado", delta=db.project)
    except:
        col3.error("Firestore inaccesible")

    # FHIR Summary
    try:
        cmd = [
            "gcloud",
            "healthcare",
            "fhir-stores",
            "list",
            "--dataset",
            "natacha-health",
            "--location",
            "us-central1",
            "--project",
            "asistente-sebastian",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        stores = json.loads(result.stdout)
        col4.metric("🧬 FHIR Stores", len(stores))
    except:
        col4.error("FHIR API no disponible")

    st.divider()
    st.info(
        "📋 Navegá entre las pestañas para ver el detalle por componente: Docker, Cloud Run, Firestore y FHIR."
    )


# =====================================================
# 🐳 TAB 2 - DOCKER LOCAL
# =====================================================
with tab_docker:
    st.header("🐳 Contenedores Docker locales")

    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)

        if containers:
            rows = []
            for c in containers:
                ports = []
                if c.attrs["NetworkSettings"]["Ports"]:
                    for private, mapping in c.attrs["NetworkSettings"]["Ports"].items():
                        if mapping:
                            for m in mapping:
                                ports.append(f"{m['HostPort']}→{private}")
                rows.append(
                    {
                        "Nombre": c.name,
                        "Imagen": c.image.tags[0] if c.image.tags else "(sin tag)",
                        "Estado": (
                            "🟢 Activo" if c.status == "running" else "🔴 Detenido"
                        ),
                        "Puertos": ", ".join(ports) or "-",
                        "Red": (
                            list(c.attrs["NetworkSettings"]["Networks"].keys())[0]
                            if c.attrs["NetworkSettings"]["Networks"]
                            else "-"
                        ),
                        "Inicio": c.attrs["State"]["StartedAt"][:19].replace("T", " "),
                    }
                )
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay contenedores locales activos o configurados.")

    except Exception as e:
        st.error(f"Error al leer Docker: {e}")

# =====================================================
# ☁️ TAB 3 - CLOUD RUN
# =====================================================
with tab_cloudrun:
    st.header("☁️ Servicios Cloud Run")

    try:
        cmd = [
            "gcloud",
            "run",
            "services",
            "list",
            "--platform",
            "managed",
            "--project",
            "asistente-sebastian",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        services = json.loads(result.stdout)

        if services:
            table = []
            for s in services:
                meta = s.get("metadata", {})
                status = s.get("status", {})
                table.append(
                    {
                        "Servicio": meta.get("name", "-"),
                        "Región": s.get("location", "-"),
                        "Último despliegue": meta.get("creationTimestamp", "-"),
                        "URL": status.get("url", "-"),
                        "Estado": (
                            "🟢 READY" if "Ready" in str(status) else "⚪ Desconocido"
                        ),
                    }
                )
            st.dataframe(pd.DataFrame(table), use_container_width=True)
        else:
            st.warning("No se encontraron servicios activos en Cloud Run.")

    except Exception as e:
        st.error(f"Error al obtener datos de Cloud Run: {e}")

# =====================================================
# 🔥 TAB 4 - FIRESTORE
# =====================================================
with tab_firestore:
    st.header("🔥 Firestore (Proyecto: asistente-sebastian)")

    try:
        db = firestore.Client()
        collections = list(db.collections())
        st.success(f"Conectado a Firestore ({db.project}) ✅")
        st.write(f"📚 Se encontraron **{len(collections)}** colecciones.")
        if collections:
            st.dataframe(pd.DataFrame({"Colección": [c.id for c in collections]}))
    except Exception as e:
        st.error(f"Error al conectar con Firestore: {e}")

# =====================================================
# 🧬 TAB 5 - FHIR
# =====================================================
with tab_fhir:
    st.header("🧬 FHIR Dataset (natacha-health)")

    try:
        cmd = [
            "gcloud",
            "healthcare",
            "fhir-stores",
            "list",
            "--dataset",
            "natacha-health",
            "--location",
            "us-central1",
            "--project",
            "asistente-sebastian",
            "--format",
            "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        stores = json.loads(result.stdout)

        if stores:
            rows = [
                {"Store": s["name"], "Versión": s["version"], "Estado": "🟢 Activo"}
                for s in stores
            ]
            st.dataframe(pd.DataFrame(rows))
        else:
            st.warning("No se encontraron FHIR stores en el dataset 'natacha-health'.")
    except Exception as e:
        st.error(f"Error al obtener información FHIR: {e}")
