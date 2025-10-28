import streamlit as st
import pandas as pd
import time
from google.cloud import firestore
from datetime import datetime, timedelta, UTC
import matplotlib.pyplot as plt

# Configuración general del dashboard
st.set_page_config(page_title="Natacha — Centro de Comando", layout="wide")

# Recarga automática cada 30 segundos
st_autorefresh = st.experimental_rerun if hasattr(st, "experimental_rerun") else None
st.markdown(
    """
    <meta http-equiv="refresh" content="30">
    """,
    unsafe_allow_html=True
)

# Título principal
st.title("🤖 Natacha — Centro de Comando Autónomo")
st.caption("Supervisión total, memoria viva y aprendizaje continuo.")

# Conexión a Firestore
db = firestore.Client()

# Cargar datos de Firestore
def load_data():
    system_health = list(
        db.collection("system_health")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(200)
        .stream()
    )
    data = [doc.to_dict() for doc in system_health]
    return pd.DataFrame(data)

# Intentar cargar datos
try:
    df = load_data()
except Exception as e:
    st.error(f"Error al conectar con Firestore: {e}")
    st.stop()

# Asegurar compatibilidad con timestamps
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
else:
    df["timestamp"] = pd.NaT

# Calcular métricas principales
total_servicios = df["service"].nunique() if not df.empty else 0
fallos = df[df["status"].str.contains("❌", na=False)].shape[0]
progreso = int((1 - fallos / max(total_servicios, 1)) * 100)

# Mostrar métricas
st.subheader("🧭 Estado General del Sistema")
col1, col2, col3 = st.columns(3)
col1.metric("Servicios activos", total_servicios)
col2.metric("Fallos detectados", fallos)
col3.metric("Progreso global", f"{progreso}%")

if fallos > 0:
    st.error(f"🔴 {fallos} servicio(s) fallando — atención requerida.")
else:
    st.success("🟢 Todos los servicios operativos.")

st.caption(f"Última actualización: {datetime.now(UTC).isoformat()} UTC")

# Filtrar últimos 24h
last_24h = datetime.now(UTC) - timedelta(hours=24)
df = df[df["timestamp"] >= last_24h]

# Mostrar gráfico de uptime
st.subheader("📈 Histórico de Uptime (últimas 24h)")
if not df.empty:
    df_sorted = df.sort_values("timestamp")
    fig, ax = plt.subplots(figsize=(10, 4))
    for service, group in df_sorted.groupby("service"):
        ax.plot(group["timestamp"], range(len(group)), marker="o", linestyle="-", label=service)
    ax.legend()
    ax.set_xlabel("Hora")
    ax.set_ylabel("Eventos registrados")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("No hay registros de las últimas 24 horas.")

# Mostrar registros recientes
st.subheader("🧾 Últimos registros de salud")
if not df.empty:
    st.dataframe(df[["timestamp", "service", "status", "source"]].sort_values("timestamp", ascending=False))
else:
    st.warning("Sin datos disponibles en Firestore.")

st.markdown("---")
st.caption("Natacha Dashboard — versión estable | Actualización automática cada 30s")
