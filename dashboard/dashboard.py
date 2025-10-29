import streamlit as st
from datetime import datetime, timezone
import os, sys
import requests
import pandas as pd

# === Fix para ejecutar desde run_dashboard.py o streamlit directo ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ✅ Imports internos del dashboard
from dashboard.system_health import main as system_health
from dashboard.infra_control import docker_monitor, cloud_monitor, system, infra_audit

# ==========================
# 🎨 CONFIGURACIÓN INICIAL
# ==========================
st.set_page_config(page_title="Natacha Dashboard", layout="wide")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/ab/Logo_Turing.svg", width=180)
st.sidebar.title("🌐 Panel Natacha")

# ==========================
# 🌍 BACKEND GLOBAL
# ==========================
BACKEND_URL = os.getenv("NATACHA_HEALTH_URL", "https://natacha-health-monitor-422255208682.us-central1.run.app")

# ==========================
# 🟢 SEMÁFORO DE ESTADO GLOBAL
# ==========================
def get_global_status():
    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("data", data) if isinstance(data, dict) else data
            if not history:
                return "⚪", "Sin datos"
            latest = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
            disk = latest.get("disk_usage", "0%")
            usage = float(str(disk).replace("%", "").strip())
            if usage > 90:
                return "🔴", f"Disco crítico ({usage}%)"
            elif usage > 75:
                return "🟠", f"Disco alto ({usage}%)"
            else:
                return "🟢", f"Todo estable ({usage}%)"
        return "⚪", "Sin conexión"
    except Exception:
        return "⚪", "Error de conexión"

status_icon, status_text = get_global_status()
st.sidebar.markdown(f"### Estado General: {status_icon}")
st.sidebar.caption(status_text)

# ==========================
# ⚠️ ALERTA LATERAL DE AUTO-HEALER
# ==========================
def get_auto_healer_status():
    """Verifica si hubo intervenciones automáticas recientes."""
    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
        if resp.status_code != 200:
            return "⚪", "No hay conexión con monitor"
        data = resp.json()
        history = data.get("data", data) if isinstance(data, dict) else data
        if not history:
            return "⚪", "Sin registros de intervención"
        
        # Filtrar diagnósticos con más de 24 h
        latest = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
        ts = pd.to_datetime(latest.get("timestamp"), errors="coerce")
        if pd.isna(ts):
            return "⚪", "Sin timestamp válido"
        age_h = (datetime.now(timezone.utc) - ts.tz_localize("UTC")).total_seconds() / 3600

        if age_h < 1:
            return "🟢", f"Última intervención hace {age_h:.1f} h"
        elif age_h < 6:
            return "🟠", f"Última intervención hace {age_h:.1f} h"
        else:
            return "🔴", f"Sin actividad automática desde hace {age_h:.1f} h"
    except Exception:
        return "⚪", "Error consultando Auto-Healer"

healer_icon, healer_text = get_auto_healer_status()
st.sidebar.markdown(f"### Auto-Healer: {healer_icon}")
st.sidebar.caption(healer_text)
st.sidebar.markdown("---")

# ==========================
# 🧭 NAVEGACIÓN
# ==========================
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
        "🧩 Auto-Healing & Control Inteligente",
        "⚙️ Configuración"
    ]
)

# ==========================
# ⏱️ FRECUENCIA DE REFRESCO
# ==========================
refresh_interval = st.sidebar.selectbox(
    "⏱️ Frecuencia de actualización",
    ["30 seg", "1 min", "5 min", "10 min"],
    index=1
)
interval_seconds = {"30 seg": 30, "1 min": 60, "5 min": 300, "10 min": 600}[refresh_interval]
st.sidebar.markdown("---")

# ==========================
# 🌍 ESTADO GENERAL
# ==========================
if page == "🌍 Estado General":
    st.header("🌍 Estado General de la Infraestructura Natacha")

    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("data", data) if isinstance(data, dict) else data
            if len(history) == 0:
                st.warning("No hay datos recientes disponibles.")
            else:
                df = pd.DataFrame(history)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                latest = df.sort_values("timestamp", ascending=False).head(1).iloc[0]

                disk = latest.get("disk_usage", "N/A")
                env = latest.get("environment", "desconocido")
                ts = latest.get("timestamp")

                st.markdown(f"### 🕒 Último diagnóstico: {ts.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**🌤️ Entorno:** `{env}` | **💽 Uso de disco:** `{disk}`")

                disk_num = float(str(disk).replace('%', '')) if "%" in str(disk) else 0
                if disk_num > 90:
                    st.error("🚨 Riesgo crítico: uso de disco superior al 90%")
                elif disk_num > 75:
                    st.warning("⚠️ Atención: uso de disco elevado")
                else:
                    st.success("🟢 Sistema operativo estable y sin alertas críticas")

                st.markdown("---")
                st.subheader("📋 Últimos registros de diagnósticos")
                st.dataframe(df.sort_values("timestamp", ascending=False).head(10), use_container_width=True)

        else:
            st.error(f"❌ Error {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"🚨 Error al conectar con el monitor: {e}")

# ==========================
# 🩺 PANEL DE SALUD
# ==========================
elif page == "🩺 Salud del Sistema":
    st.header("🩺 Panel de Salud del Sistema Natacha")
    st.caption("Monitoreo en tiempo real desde Firestore o diagnóstico local.")
    system_health()

# ==========================
# 📈 HISTÓRICO DE RENDIMIENTO
# ==========================
elif page == "📈 Histórico de Rendimiento":
    st.header("📈 Histórico de Rendimiento del Sistema")
    st.caption("Datos obtenidos desde Cloud Run / Firestore con alertas de estado")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Ejecutar nuevo diagnóstico"):
            try:
                run = requests.post(f"{BACKEND_URL}/run_auto_infra_check", timeout=15)
                if run.status_code == 200:
                    st.success("✅ Diagnóstico ejecutado y almacenado correctamente")
                else:
                    st.warning(f"⚠️ No se pudo ejecutar el diagnóstico ({run.status_code})")
            except Exception as e:
                st.error(f"Error al ejecutar el diagnóstico: {e}")

    try:
        resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("data", data) if isinstance(data, dict) else data
            if len(history) > 0:
                df = pd.DataFrame(history)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                df = df.sort_values("timestamp", ascending=False)
                st.success(f"✅ {len(df)} registros cargados desde Firestore")

                latest = df.iloc[0]
                disk_usage = latest.get("disk_usage", "0%")
                env = latest.get("environment", "desconocido")
                ts = latest.get("timestamp")

                alerts = []
                try:
                    usage_num = float(str(disk_usage).replace("%", "").strip())
                    if usage_num > 80:
                        alerts.append(f"⚠️ Uso de disco alto: {usage_num}%")
                    elif usage_num > 60:
                        alerts.append(f"🟡 Uso de disco moderado: {usage_num}%")
                    else:
                        alerts.append(f"✅ Uso de disco saludable: {usage_num}%")
                except Exception:
                    alerts.append("⚠️ No se pudo analizar el uso de disco")

                if ts and (datetime.now(timezone.utc) - ts.tz_localize("UTC")).total_seconds() > 86400:
                    alerts.append("⚠️ Último diagnóstico tiene más de 24 h")

                if env == "cloudrun":
                    alerts.append("☁️ Diagnóstico desde entorno Cloud Run")
                else:
                    alerts.append("💻 Diagnóstico desde entorno local")

                st.markdown("### 🔔 Estado actual del sistema")
                for a in alerts:
                    if "⚠️" in a:
                        st.warning(a)
                    elif "🟡" in a:
                        st.info(a)
                    else:
                        st.success(a)

                st.markdown("---")
                st.subheader("📋 Registros históricos de infraestructura")
                st.dataframe(df, use_container_width=True)

                if "disk_usage" in df.columns:
                    df["disk_usage_pct"] = df["disk_usage"].astype(str).str.replace("%", "").astype(float)
                    st.line_chart(df.set_index("timestamp")["disk_usage_pct"], height=300)
            else:
                st.warning("⚠️ No se encontraron registros históricos.")
        else:
            st.error(f"❌ Error {resp.status_code}: {resp.text}")
    except Exception as e:
        st.error(f"🚨 No se pudo conectar al backend: {e}")

# === RESTO DE SECCIONES ===
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

elif page == "🧩 Auto-Healing & Control Inteligente":
    from dashboard.infra_control import auto_healer_panel
    auto_healer_panel.show()

elif page == "⚙️ Configuración":
    st.header("⚙️ Configuración del Dashboard y Variables del Sistema")
    st.text("Aquí podrás ajustar parámetros globales y credenciales (en desarrollo).")

# ==========================
# 🕓 PIE DE PÁGINA
# ==========================
st.sidebar.markdown("---")
st.sidebar.caption(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.sidebar.caption("Desarrollado con ❤️ para Natacha Cloud Infrastructure v2")
