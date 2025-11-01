import streamlit as st
from datetime import datetime, timezone
import os, sys, json
import requests
import pandas as pd

# === Fix path ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ==========================
# 🎨 CONFIGURACIÓN INICIAL
# ==========================
st.set_page_config(page_title="Natacha Dashboard", layout="wide")

# --- sidebar brand image ---
local_img = os.path.join(os.path.dirname(__file__), "static", "natacha-llvc.png")
fallback_img = "https://raw.githubusercontent.com/sebastianatenor/assets/main/natacha-placeholder.png"
try:
    if os.path.exists(local_img):
        st.sidebar.image(local_img, width=210)
    else:
        st.sidebar.image(fallback_img, width=210)
except Exception:
    pass

st.sidebar.title("🌐 Panel Natacha")

# ==========================
# 🔗 ENDPOINTS / CONFIG
# ==========================
NATACHA_API = os.getenv(
    "NATACHA_API_URL",
    "https://natacha-api-422255208682.us-central1.run.app"
)
HEALTH_MONITOR = os.getenv(
    "NATACHA_HEALTH_URL",
    "https://natacha-health-monitor-422255208682.us-central1.run.app"
)

# ==========================
# 🔧 HELPERS
# ==========================
def fetch_json(url: str, default=None, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return default

def parse_firestore_list(raw):
    """
    Firestore runQuery devuelve una lista de objetos con document/readTime.
    Esto lo pasamos a una lista "plana".
    """
    results = []
    for item in raw or []:
        doc = item.get("document")
        if not doc:
            continue
        fields = doc.get("fields", {})
        row = {}
        for k, v in fields.items():
            # string
            if "stringValue" in v:
                row[k] = v["stringValue"]
            # number
            elif "integerValue" in v:
                row[k] = int(v["integerValue"])
            elif "doubleValue" in v:
                row[k] = float(v["doubleValue"])
            # array
            elif "arrayValue" in v:
                row[k] = v["arrayValue"].get("values", [])
            else:
                row[k] = v
        results.append(row)
    return results

# ==========================
# 📥 DATOS DE INFRA
# ==========================
def load_infra_data():
    """
    1) intenta Cloud Run health monitor → /infra_history_cloud
    2) si está vacío, intenta leer Firestore (colección infra_history) vía API del monitor
    3) si sigue vacío → None
    """
    # 1) lo que ya probaste
    cloud = fetch_json(f"{HEALTH_MONITOR}/infra_history_cloud", default=None)
    if cloud and isinstance(cloud, dict) and cloud.get("data"):
        return {
            "source": "cloud",
            "rows": cloud["data"]
        }

    # 2) el monitor SI está guardando en 'infra_history' (lo vimos con curl)
    # agregamos un endpoint "legacy" que muchos de tus scripts usan: /infra_history
    history = fetch_json(f"{HEALTH_MONITOR}/infra_history", default=None)
    if history and isinstance(history, dict) and history.get("data"):
        return {
            "source": "infra_history",
            "rows": history["data"]
        }

    # 3) nada
    return None

def load_operational_data():
    data = fetch_json(f"{NATACHA_API}/dashboard/data", default=None)
    return data

# ==========================
# 🧭 NAVEGACIÓN
# ==========================
page = st.sidebar.radio(
    "Navegación",
    [
        "🌍 Estado General",
        "🩺 Salud del Sistema",
        "🚀 Control de Servicios",
        "🧩 Auditoría Global de Infraestructura",
        "⚙️ Configuración"
    ]
)

# ==========================
# 🌍 ESTADO GENERAL
# ==========================
if page == "🌍 Estado General":
    st.header("🌍 Estado General de la Infraestructura Natacha")

    infra = load_infra_data()
    if infra and infra["rows"]:
        # tenemos data real de infra
        rows = infra["rows"]
        df = pd.DataFrame(rows)
        st.success(f"✅ Datos de infraestructura desde: **{infra['source']}** ({len(df)} registros)")
        # último
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp", ascending=False)
        latest = df.iloc[0]
        st.markdown(f"**🕒 Último diagnóstico:** {latest.get('timestamp')}")
        st.markdown(f"**📦 Entorno:** {latest.get('environment','-')} — **💽 Disco:** {latest.get('disk_usage','-')}")
        # mostrar tabla
        st.subheader("📋 Registros recientes")
        st.dataframe(df, width="stretch")
    else:
        st.warning("🛠️ Monitor de infraestructura ONLINE pero sin registros todavía.")
        st.info("Esto pasa cuando el servicio de health se desplegó pero todavía no escribió en Firestore.")
        # fallback operativo
        op = load_operational_data()
        if op:
            st.markdown("—")
            st.markdown("### 💼 Modo OPERATIVO (proyectos / tareas) — datos desde Natacha API")
            st.metric("Proyectos", op.get("totals",{}).get("projects",0))
            st.metric("Tareas", op.get("totals",{}).get("tasks",0))
            st.metric("Memorias", op.get("totals",{}).get("memories",0))
            st.write("📋 Proyectos cargados")
            for p in op.get("projects",[]):
                st.write(f"• **{p['name']}** — {p['pending_tasks']} pendiente(s)")
                st.caption(f"Urgente: {p['urgent_title']} | vence: {p['urgent_due']}")
        else:
            st.error("❌ No se pudo obtener ni infraestructura ni datos operativos.")

# ==========================
# 🩺 SALUD DEL SISTEMA
# ==========================
elif page == "🩺 Salud del Sistema":
    st.header("🩺 Panel de Salud del Sistema Natacha")
    st.caption("Monitoreo en tiempo real desde Firestore (`system_health`).")

    # intentamos leer directamente al monitor
    health = fetch_json(f"{HEALTH_MONITOR}/system_health", default=None)
    if health and isinstance(health, dict) and health.get("data"):
        data = health["data"]
        st.success(f"✅ {len(data)} servicios reportando")
        for svc in data:
            name = svc.get("service","(sin nombre)")
            status = svc.get("status","-")
            ts = svc.get("timestamp","-")
            cpu = svc.get("cpu") or svc.get("cpu_pct")
            mem = svc.get("mem") or svc.get("mem_pct")
            col1, col2, col3, col4 = st.columns([2,2,1,1])
            col1.write(f"🟢 **{name}**")
            col2.write(f"⏱️ {ts}")
            col3.write(f"CPU: {cpu if cpu is not None else '—'}")
            col4.write(f"MEM: {mem if mem is not None else '—'}")
    else:
        # fallback a datos operativos
        st.warning("⚠️ No se pudieron obtener datos de salud. Mostrando estado operativo.")
        op = load_operational_data()
        if op:
            st.metric("Proyectos", op.get("totals",{}).get("projects",0))
            st.metric("Tareas", op.get("totals",{}).get("tasks",0))
        else:
            st.info("No hay datos operativos tampoco.")

# ==========================
# 🚀 CONTROL DE SERVICIOS
# ==========================
elif page == "🚀 Control de Servicios":
    st.header("🚀 Control de Servicios Locales y Cloud")
    st.info("Acá podemos enchufar lo que ya tenías en dashboard/infra_control/system.py y docker_monitor.py")
    try:
        from dashboard.infra_control import system
        system.show()
    except Exception as e:
        st.error(f"No se pudo cargar panel de sistema: {e}")

# ==========================
# 🧩 AUDITORÍA
# ==========================
elif page == "🧩 Auditoría Global de Infraestructura":
    st.header("🧩 Auditoría Global de Infraestructura")
    try:
        from dashboard.infra_control import infra_audit
        infra_audit.show()
    except Exception as e:
        st.error(f"No se pudo cargar auditoría: {e}")

# ==========================
# ⚙️ CONFIG
# ==========================
elif page == "⚙️ Configuración":
    st.header("⚙️ Configuración del Dashboard")
    st.code(json.dumps({
        "NATACHA_API": NATACHA_API,
        "HEALTH_MONITOR": HEALTH_MONITOR
    }, indent=2))

# footer
st.sidebar.markdown("---")
st.sidebar.caption(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
st.sidebar.caption("LLVC · Natacha Cloud · dashboard unificado")
