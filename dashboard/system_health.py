import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from google.cloud import firestore
import time
import math

# -------------------------------
# 🩺 Panel de Salud del Sistema Natacha
# -------------------------------
st.set_page_config(page_title="Panel de Salud Natacha", layout="wide", page_icon="🩺")
st.title("🩺 Panel de Salud del Sistema Natacha")
st.write("Monitoreo automático en tiempo real desde Firestore (colección: `system_health`)")

# -------------------------------
# ⚙️ Configuración de refresco
# -------------------------------
refresh_options = {"30s": 30, "1 min": 60, "5 min": 300}
interval_label = st.sidebar.selectbox("⏱️ Frecuencia de actualización", list(refresh_options.keys()), index=1)
REFRESH_INTERVAL = refresh_options[interval_label]

# -------------------------------
# 🔥 Conectar a Firestore
# -------------------------------
db = firestore.Client()

with st.spinner("💫 Obteniendo datos de Firestore..."):
    try:
        docs = list(db.collection("system_health").stream())
        data = [doc.to_dict() for doc in docs if doc.to_dict()]
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error al leer Firestore: {e}")
        st.stop()

if df.empty:
    st.warning("⚠️ No hay datos disponibles en Firestore.")
    st.stop()

# -------------------------------
# 🧩 Procesamiento de datos
# -------------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
df = df.sort_values("timestamp", ascending=False).drop_duplicates(subset="service", keep="first")

# Convertir NaN en None para evitar errores de barra de progreso
df = df.where(pd.notnull(df), None)

now = datetime.now(timezone.utc)
st.caption(f"🕒 Última actualización: {now.strftime('%H:%M:%S UTC')} — se actualiza cada {interval_label}")

# -------------------------------
# 📊 Mostrar servicios
# -------------------------------
for _, row in df.iterrows():
    service = row.get("service", "❓")
    status = str(row.get("status", "Desconocido"))
    cpu = row.get("cpu")
    mem = row.get("mem")
    ts = row.get("timestamp")

    # Validar CPU y MEM
    def safe_float(x):
        try:
            if x is None:
                return None
            val = float(x)
            if math.isnan(val) or val < 0:
                return None
            return val
        except Exception:
            return None

    cpu = safe_float(cpu)
    mem = safe_float(mem)

    # Calcular antigüedad del reporte
    if pd.notna(ts):
        age_min = (now - ts).total_seconds() / 60
        time_str = f"{ts.strftime('%H:%M:%S')} UTC ({age_min:.1f} min atrás)"
    else:
        time_str = "Sin timestamp"
        age_min = None

    # Determinar color de estado
    if "online" in status.lower():
        color = "🟢"
    elif "alert" in status.lower() or "degraded" in status.lower():
        color = "🟠"
    else:
        color = "🔴"

    # Mostrar datos
    st.subheader(f"{color} {service}")
    st.write(f"**Estado:** {status}")
    st.caption(f"⏱️ Último reporte: {time_str}")

    # Barras de progreso seguras
    if cpu is not None:
        st.progress(min(max(cpu / 100, 0.0), 1.0), text=f"CPU: {cpu:.1f}%")
    else:
        st.text("⚙️ CPU: Sin datos")

    if mem is not None:
        st.progress(min(max(mem / 100, 0.0), 1.0), text=f"Memoria: {mem:.1f}%")
    else:
        st.text("💾 Memoria: Sin datos")

    # Alertas de inactividad
    if age_min is not None and age_min > 10:
        st.error(f"🚨 Sin reportes recientes ({age_min:.1f} min sin actualizar)")

    st.divider()

# -------------------------------
# 🔄 Auto-refresh simple
# -------------------------------
st.info(f"🔄 Refrescando cada {REFRESH_INTERVAL} segundos…")
time.sleep(REFRESH_INTERVAL)
if hasattr(st, "rerun"):
    st.rerun()
else:
    st.experimental_rerun()

def main():
    """Punto de entrada de salud del sistema."""
    print("🩺 system_health.main() ejecutado correctamente.")
