import streamlit as st
from dashboard import auth
auth.check_login()

from datetime import datetime, timezone
import os, sys
import requests
import pandas as pd
from PIL import Image

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

# ==========================
# 🔐 AUTH SÚPER SIMPLE
# ==========================
DASH_USER = os.getenv("DASH_USER", "llvc")
DASH_PASS = os.getenv("DASH_PASS", "natacha2025")

def check_password():
    if "auth_ok" not in st.session_state:
        st.session_state["auth_ok"] = False

    if st.session_state["auth_ok"]:
        return True

    with st.sidebar.form("login", clear_on_submit=False):
        user = st.text_input("User", value="", key="__user")
        pwd = st.text_input("Password", value="", type="password", key="__pwd")
        ok = st.form_submit_button("Login")

    if ok and user == DASH_USER and pwd == DASH_PASS:
        st.session_state["auth_ok"] = True
        return True

    st.stop()

# 👇 esto fuerza que haya login antes de mostrar el resto
check_password()

# --- sidebar brand image ---
local_img = os.path.join(os.path.dirname(__file__), "static", "natacha-llvc.png")
fallback_img = "https://raw.githubusercontent.com/sebastianatenor/assets/main/natacha-placeholder.png"

try:
    if os.path.exists(local_img):
        logo_img = Image.open(local_img)
        st.sidebar.image(logo_img, width=220)
    else:
        st.sidebar.image(fallback_img, width=210)
except Exception:
    st.sidebar.image(fallback_img, width=210)

# --- corporate signature ---
st.sidebar.markdown(
    """
    <style>
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: 200px 0; }
    }
    .shimmer {
        background: linear-gradient(90deg, #D4AF37 0%, #F6E27F 50%, #D4AF37 100%);
        background-size: 400px 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s infinite linear;
        font-weight: bold;
        font-size: 17px;
    }
    </style>

    <div style='text-align:center; margin-top:-10px;'>
        <span class='shimmer'>LLVC Infrastructure Console</span><br>
        <span style='font-size:14px; color:gray;'>powered by <b>Natacha</b></span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
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

                st.markdown(f"### 🕒 Último diagnóstico: {ts}")
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
    st.code({
        "BACKEND_URL": BACKEND_URL,
        "DASH_USER": DASH_USER,
        "DASH_PASS": "***"
    })
