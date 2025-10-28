import streamlit as st
from datetime import datetime, timezone
import os, sys

# === Fix para ejecutar desde run_dashboard.py o streamlit directo ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ✅ Imports absolutos y módulos internos del dashboard
from dashboard.system_health import main as system_health
from dashboard.infra_control import docker_monitor, cloud_monitor, system, infra_audit

# ==========================
# 🎨 ENCABEZADO Y ESTILO
# ==========================
st.set_page_config(page_title="Natacha Dashboard", layout="wide")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_Turing.svg", width=180)
st.sidebar.title("🌐 Panel Natacha")

# ==========================
# 🧭 NAVEGACIÓN
# ==========================
page = st.sidebar.radio(
    "Navegación",
    [
        "🩺 Salud del Sistema",
        "📈 Histórico de Rendimiento",
        "🧠 Memoria y Firestore",
        "🚀 Control de Servicios",
        "🐳 Docker Local",
        "☁️ Infraestructura Cloud",
        "🧩 Auditoría Global de Infraestructura",
        "⚙️ Configuración"
    ]
)

# ==========================
# 🕒 FRECUENCIA DE REFRESCO
# ==========================
refresh_interval = st.sidebar.selectbox(
    "⏱️ Frecuencia de actualización",
    ["30 seg", "1 min", "5 min", "10 min"],
    index=1
)
interval_seconds = {"30 seg": 30, "1 min": 60, "5 min": 300, "10 min": 600}[refresh_interval]
st.sidebar.markdown("---")

# ==========================
# 📊 PÁGINAS DEL DASHBOARD
# ==========================

if page == "🩺 Salud del Sistema":
    st.header("🩺 Panel de Salud del Sistema Natacha")
    st.caption("Monitoreo automático en tiempo real desde Firestore (colección: system_health)")
    system_health()

elif page == "📈 Histórico de Rendimiento":
    st.header("📈 Histórico de Rendimiento del Sistema")

    import requests
    import pandas as pd

    BACKEND_URL = os.getenv("NATACHA_HEALTH_URL", "https://natacha-health-monitor-mkwskljrhq-uc.a.run.app")

    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history", timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                df = pd.DataFrame(data)
                st.success(f"✅ Datos cargados desde {BACKEND_URL}")

                # Mostrar tabla
                st.subheader("📊 Registros históricos de infraestructura")
                st.dataframe(df)

                # Convertir timestamp
                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

                # === GRÁFICO 1: Uso de disco ===
                if "disk_usage" in df.columns:
                    st.subheader("💽 Uso de disco (%) a lo largo del tiempo")
                    try:
                        df["disk_usage"] = df["disk_usage"].astype(str).str.replace("%", "").astype(float)
                        st.line_chart(df.set_index("timestamp")["disk_usage"])
                    except Exception as e:
                        st.warning(f"No se pudo graficar el uso de disco: {e}")

                # === GRÁFICO 2: Servicios Cloud Run ===
                if "cloud_run_services" in df.columns:
                    st.subheader("☁️ Servicios Cloud Run activos")
                    st.bar_chart(df.set_index("timestamp")["cloud_run_services"])

                # === GRÁFICO 3: VMs y Contenedores ===
                cols = st.columns(2)

                with cols[0]:
                    if "vm_status" in df.columns:
                        st.subheader("🖥️ Máquinas virtuales activas")
                        try:
                            df["vm_count"] = df["vm_status"].apply(lambda x: len(x) if isinstance(x, list) else 0)
                            st.line_chart(df.set_index("timestamp")["vm_count"])
                        except Exception as e:
                            st.warning(f"No se pudo graficar VMs: {e}")

                with cols[1]:
                    if "docker_containers" in df.columns:
                        st.subheader("🐳 Contenedores Docker detectados")
                        try:
                            df["docker_count"] = df["docker_containers"].apply(lambda x: len(x) if isinstance(x, list) else 0)
                            st.line_chart(df.set_index("timestamp")["docker_count"])
                        except Exception as e:
                            st.warning(f"No se pudo graficar contenedores: {e}")

            else:
                st.warning("⚠️ No hay registros históricos disponibles.")
        else:
            st.error(f"❌ Error {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"🚨 No se pudo conectar al backend: {e}")

elif page == "🧠 Memoria y Firestore":
    st.header("🧠 Firestore y Memoria de Natacha")
    st.info("Visualización y gestión de colecciones, entradas y logs de memoria Firestore.")

elif page == "🚀 Control de Servicios":
    st.header("🚀 Control de Servicios Locales y Cloud")
    system.show()

elif page == "🐳 Docker Local":
    st.header("🐳 Monitoreo de Contenedores Docker Locales")
    docker_monitor.show()

elif page == "☁️ Infraestructura Cloud":
    st.header("☁️ Estado de la Infraestructura Cloud (Google Cloud)")
    cloud_monitor.show()

elif page == "🧩 Auditoría Global de Infraestructura":
    st.header("🧩 Auditoría Global de Infraestructura")
    infra_audit.show()

elif page == "⚙️ Configuración":
    st.header("⚙️ Configuración del Dashboard y Variables del Sistema")
    st.text("Aquí podrás ajustar parámetros globales y credenciales (en desarrollo).")

# ==========================
# 🕓 PIE DE PÁGINA
# ==========================
st.sidebar.markdown("---")
st.sidebar.caption(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.sidebar.caption("Desarrollado con ❤️ para Natacha Cloud Infrastructure v2")
