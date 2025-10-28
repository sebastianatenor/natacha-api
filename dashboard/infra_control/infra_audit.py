import streamlit as st
import subprocess
from datetime import datetime, timezone

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

def show():
    st.title("🌍 Auditoría Completa de Infraestructura Natacha")

    st.subheader("🐳 Docker Containers")
    st.code(run_cmd("docker ps -a"))

    st.subheader("🐳 Docker Images")
    st.code(run_cmd("docker images"))

    st.subheader("🌐 Docker Networks")
    st.code(run_cmd("docker network ls"))

    st.subheader("☁️ Google Cloud Run Services")
    st.code(run_cmd("gcloud run services list --platform managed --project asistente-sebastian"))

    st.subheader("🔥 Firestore Collections")
    st.code(run_cmd("python3 -c 'from google.cloud import firestore; print([c.id for c in firestore.Client().collections()])'"))

    st.subheader("🧬 Healthcare Datasets")
    st.code(run_cmd("gcloud healthcare datasets list --project asistente-sebastian"))

    st.caption(f"Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
