import pandas as pd
from datetime import datetime, timezone
from google.cloud import firestore
import math

def main():
    import streamlit as st

    st.subheader("🩺 Panel de Salud del Sistema Natacha")
    st.caption("Monitoreo automático en tiempo real desde Firestore (colección: `system_health`)")

    # -------------------------------
    # ⚙️ Conexión a Firestore
    # -------------------------------
    try:
        db = firestore.Client()
        docs = list(db.collection("system_health").stream())
        data = [doc.to_dict() for doc in docs if doc.to_dict()]
        df = pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error al leer Firestore: {e}")
        return

    if df.empty:
        st.warning("⚠️ No hay datos disponibles en Firestore.")
        return

    # -------------------------------
    # 🧩 Procesamiento de datos
    # -------------------------------
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.sort_values("timestamp", ascending=False).drop_duplicates(subset="service", keep="first")
    df = df.where(pd.notnull(df), None)

    now = datetime.now(timezone.utc)
    st.caption(f"🕒 Última actualización: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # -------------------------------
    # 📊 Mostrar servicios
    # -------------------------------
    for _, row in df.iterrows():
        service = row.get("service", "❓")
        status = str(row.get("status", "Desconocido"))
        cpu = row.get("cpu")
        mem = row.get("mem")
        ts = row.get("timestamp")

        # Conversión segura
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
        st.markdown(f"### {color} {service}")
        st.write(f"**Estado:** {status}")
        st.caption(f"⏱️ Último reporte: {time_str}")

        if cpu is not None:
            st.progress(min(max(cpu / 100, 0.0), 1.0), text=f"CPU: {cpu:.1f}%")
        else:
            st.text("⚙️ CPU: Sin datos")

        if mem is not None:
            st.progress(min(max(mem / 100, 0.0), 1.0), text=f"Memoria: {mem:.1f}%")
        else:
            st.text("💾 Memoria: Sin datos")

        if age_min is not None and age_min > 10:
            st.error(f"🚨 Sin reportes recientes ({age_min:.1f} min sin actualizar)")

        st.divider()

    st.success("✅ Datos actualizados correctamente desde Firestore.")
