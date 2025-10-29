import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone
import os, sys

# === Fix rutas ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# === Imports internos ===
from dashboard.system_health import main as system_health
from dashboard.infra_control import docker_monitor, cloud_monitor, system, infra_audit

# === Configuración general ===
st.set_page_config(page_title="Natacha Dashboard", layout="wide", page_icon="🌐")

BACKEND_URL = os.getenv("NATACHA_HEALTH_URL", "https://natacha-health-monitor-mkwskljrhq-uc.a.run.app")

# === Estado global (semáforo simplificado) ===
def global_status():
    try:
        r = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=8)
        if r.status_code != 200:
            return "⚪", "Sin conexión"
        data = r.json()
        history = data.get("data", data)
        if not history:
            return "⚪", "Sin datos"
        last = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
        disk = float(str(last.get("disk_usage", "0")).replace("%", ""))
        if disk > 90:
            return "🔴", f"Crítico ({disk}%)"
        elif disk > 75:
            return "🟠", f"Alto ({disk}%)"
        else:
            return "🟢", f"Normal ({disk}%)"
    except Exception:
        return "⚪", "Error"

status_icon, status_text = global_status()

# === Sidebar ===
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_Turing.svg", width=180)
st.sidebar.title(f"🌐 Panel Natacha {status_icon}")
st.sidebar.caption(status_text)

page = st.sidebar.radio(
    "Navegación",
    [
        "🌍 Estado General",
        "🩺 Salud del Sistema",
        "📈 Histórico de Rendimiento",
        "🧠 Memoria y Firestore",
        "🚀 Control de Servicios",
        "🐳 Docker Local",
        "☁️ Infraestructura Cloud",
        "🧩 Auditoría Global de Infraestructura",
    ]
)

# === Estado General ===
if page == "🌍 Estado General":
    st.header("🌍 Estado General de la Infraestructura Natacha")

    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("data", data)
            if not history:
                st.warning("No hay datos recientes.")
            else:
                df = pd.DataFrame(history)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                latest = df.sort_values("timestamp", ascending=False).iloc[0]
                disk = latest.get("disk_usage", "N/A")
                env = latest.get("environment", "desconocido")
                ts = latest.get("timestamp")
                st.markdown(f"**🕒 Último diagnóstico:** {ts}")
                st.markdown(f"**💽 Uso de disco:** {disk} | **🌤️ Entorno:** {env}")

                disk_num = float(str(disk).replace("%", "")) if "%" in str(disk) else 0
                if disk_num > 90:
                    st.error("🚨 Riesgo crítico: uso de disco superior al 90%")
                elif disk_num > 75:
                    st.warning("⚠️ Atención: uso de disco elevado")
                else:
                    st.success("🟢 Sistema estable y sin alertas")

                st.markdown("---")
                st.subheader("📋 Últimos registros")
                st.dataframe(df.sort_values("timestamp", ascending=False).head(10), use_container_width=True)
        else:
            st.error(f"❌ Error {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"🚨 Error: {e}")

# === Salud del Sistema ===
elif page == "🩺 Salud del Sistema":
    st.header("🩺 Panel de Salud del Sistema Natacha")
    system_health()

# === Histórico ===
elif page == "📈 Histórico de Rendimiento":
    st.header("📈 Histórico de Rendimiento del Sistema")
    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("data", data)
            if not history:
                st.warning("No hay datos históricos.")
            else:
                df = pd.DataFrame(history)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                df = df.sort_values("timestamp", ascending=False)
                st.dataframe(df, use_container_width=True)
                if "disk_usage" in df.columns:
                    df["disk_usage_pct"] = df["disk_usage"].astype(str).str.replace("%", "").astype(float)
                    st.line_chart(df.set_index("timestamp")["disk_usage_pct"])
        else:
            st.error(f"Error {resp.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")

# === Módulos secundarios ===
elif page == "🧠 Memoria y Firestore":
    st.header("🧠 Firestore y Memoria de Natacha")
    st.info("Gestión de colecciones y registros de memoria (en desarrollo).")

elif page == "🚀 Control de Servicios":
    st.header("🚀 Control de Servicios")
    system.show()

elif page == "🐳 Docker Local":
    st.header("🐳 Monitoreo de Contenedores Docker Locales")
    docker_monitor.show()

elif page == "☁️ Infraestructura Cloud":
    st.header("☁️ Estado de la Infraestructura Cloud")
    cloud_monitor.show()

elif page == "🧩 Auditoría Global de Infraestructura":
    st.header("🧩 Auditoría Global de Infraestructura")
    infra_audit.show()

# === Footer ===
st.sidebar.markdown("---")
st.sidebar.caption(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.sidebar.caption("Desarrollado con ❤️ para Natacha Cloud Infrastructure v2")
