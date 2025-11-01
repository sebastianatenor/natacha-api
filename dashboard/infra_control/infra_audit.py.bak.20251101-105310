import streamlit as st
import subprocess
from datetime import datetime, timezone
import requests

# ============================================
# 🔧 UTILIDAD PARA EJECUTAR COMANDOS DEL SISTEMA
# ============================================
def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

# ============================================
# 🧠 PANEL PRINCIPAL DE AUDITORÍA Y AUTO-HEALER
# ============================================
def show():
    st.title("🧩 Auditoría Global y Auto-Healing de Infraestructura Natacha")

    # Tabs principales
    tabs = st.tabs(["📊 Auditoría General", "🧠 Auto-Healer (Cloud Run)"])

    # ============================================
    # 🧱 TAB 1: AUDITORÍA GENERAL
    # ============================================
    with tabs[0]:
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

        st.caption(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # ============================================
    # ⚙️ TAB 2: AUTO-HEALER VISUAL
    # ============================================
    with tabs[1]:
        st.subheader("🧠 Panel de Autocuración Inteligente")
        st.caption("Verifica los servicios Cloud Run activos y permite reiniciarlos manual o automáticamente.")

        BACKEND_URL = "https://natacha-health-monitor-422255208682.us-central1.run.app"

        col1, col2 = st.columns([2, 1])
        with col2:
            if st.button("🔁 Ejecutar Auto-Heal Manual"):
                try:
                    result = requests.post(f"{BACKEND_URL}/run_auto_infra_check", timeout=20)
                    if result.status_code == 200:
                        st.success("✅ Diagnóstico y autocuración ejecutados correctamente.")
                    else:
                        st.error(f"⚠️ Error al ejecutar el Auto-Heal: {result.status_code}")
                except Exception as e:
                    st.error(f"🚨 No se pudo conectar con el monitor: {e}")

        try:
            services_output = run_cmd("gcloud run services list --platform managed --project asistente-sebastian --format=json")
            import json
            services = json.loads(services_output)
            if services:
                st.write("### ☁️ Servicios Detectados en Cloud Run")
                for svc in services:
                    name = svc.get("metadata", {}).get("name", "N/A")
                    status = svc.get("status", {}).get("conditions", [])
                    state_icon = "🟢"
                    for cond in status:
                        if cond.get("status") == "False":
                            state_icon = "🔴"
                    st.markdown(f"**{state_icon} {name}**")

                st.caption("Pulsa el botón de arriba para reiniciar servicios con errores detectados.")
            else:
                st.warning("⚠️ No se detectaron servicios activos en Cloud Run.")
        except Exception as e:
            st.error(f"Error al obtener servicios Cloud Run: {e}")
