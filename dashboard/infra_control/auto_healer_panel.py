import streamlit as st
import requests
from datetime import datetime, timezone
import pandas as pd
import json
import os
from google.cloud import firestore

BACKEND_URL = "https://natacha-health-monitor-422255208682.us-central1.run.app"

# ============================================================
# 🔥 CLIENTE FIRESTORE
# ============================================================
def get_firestore_client():
    try:
        return firestore.Client()
    except Exception as e:
        st.warning(f"⚠️ No se pudo conectar a Firestore: {e}")
        return None


# ============================================================
# 💾 REGISTRO DE INTERVENCIÓN EN FIRESTORE
# ============================================================
def log_autoheal_event(action: str, status: str, detail: str = ""):
    client = get_firestore_client()
    if not client:
        return
    try:
        doc = {
            "action": action,
            "status": status,
            "detail": detail,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "dashboard"
        }
        client.collection("auto_healer_log").add(doc)
        st.success(f"📝 Evento registrado en Firestore ({action})")
    except Exception as e:
        st.error(f"❌ No se pudo registrar el evento: {e}")


# ============================================================
# 🚀 PANEL PRINCIPAL
# ============================================================
def show():
    st.title("🧩 Auto-Healing & Control Inteligente")
    st.caption("Monitoreo, diagnóstico y reinicio inteligente de servicios Cloud Run.")

    col1, col2, col3 = st.columns([3, 1.2, 1.2])

    # ========================================================
    # 🔍 Escanear servicios
    # ========================================================
    with col1:
        if st.button("🔍 Escanear estado de servicios"):
            with st.spinner("Consultando historial en Natacha Health Monitor..."):
                try:
                    resp = requests.get(f"{BACKEND_URL}/infra_history_cloud", timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        history = data if isinstance(data, list) else data.get("data", [])
                        if not history:
                            st.warning("⚠️ No hay registros recientes en Firestore.")
                            return

                        df = pd.DataFrame(history)
                        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                        df = df.sort_values("timestamp", ascending=False)

                        st.success(f"✅ {len(df)} registros cargados desde Firestore.")
                        st.dataframe(df.head(10), use_container_width=True)

                    else:
                        st.error(f"❌ Error {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"🚨 Error al conectar con el monitor: {e}")

    # ========================================================
    # ♻️ Ejecutar Auto-Healer remoto
    # ========================================================
    with col2:
        if st.button("♻️ Ejecutar Auto-Healer"):
            with st.spinner("Ejecutando Auto-Healer remoto..."):
                try:
                    run = requests.post(f"{BACKEND_URL}/run_auto_infra_check", timeout=15)
                    if run.status_code == 200:
                        data = run.json()
                        st.success("✅ Auto-Healer ejecutado correctamente.")
                        st.code(json.dumps(data, indent=2))
                        log_autoheal_event("auto_heal_remote", "ok", "Ejecución remota exitosa")
                    else:
                        st.warning(f"⚠️ No se pudo ejecutar el Auto-Healer ({run.status_code})")
                        log_autoheal_event("auto_heal_remote", "error", f"HTTP {run.status_code}")
                except Exception as e:
                    st.error(f"🚨 Error al ejecutar Auto-Healer: {e}")
                    log_autoheal_event("auto_heal_remote", "error", str(e))

    # ========================================================
    # 🔁 Reinicio manual de un servicio
    # ========================================================
    with col3:
        st.markdown("### 🔧 Reinicio manual")
        service_name = st.text_input("Nombre del servicio Cloud Run", "")
        if st.button("🚀 Reiniciar servicio"):
            if not service_name.strip():
                st.warning("⚠️ Ingresá un nombre de servicio válido.")
            else:
                with st.spinner(f"Reiniciando servicio `{service_name}`..."):
                    try:
                        cmd = f"gcloud run services update-traffic {service_name} --to-latest --platform managed --region us-central1 --project asistente-sebastian"
                        result = os.popen(cmd).read()
                        st.success(f"✅ Servicio `{service_name}` reiniciado.")
                        st.text(result)
                        log_autoheal_event("manual_restart", "ok", f"Servicio: {service_name}")
                    except Exception as e:
                        st.error(f"❌ Error al reiniciar {service_name}: {e}")
                        log_autoheal_event("manual_restart", "error", str(e))

    st.markdown("---")

    # ========================================================
    # 📊 Historial de intervenciones
    # ========================================================
    st.subheader("📊 Historial de Intervenciones Auto-Healer")

    client = get_firestore_client()
    if client:
        try:
            docs = (
                client.collection("auto_healer_log")
                .order_by("timestamp", direction=firestore.Query.DESCENDING)
                .limit(50)
                .stream()
            )
            records = [doc.to_dict() for doc in docs]
            if records:
                df = pd.DataFrame(records)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                st.dataframe(df, use_container_width=True)
                df["count"] = 1
                chart_data = df.groupby(df["timestamp"].dt.date)["count"].sum()
                st.line_chart(chart_data, height=250)
            else:
                st.info("📭 No hay registros de intervenciones aún.")
        except Exception as e:
            st.error(f"🚨 Error al leer historial de Firestore: {e}")

    st.info(f"🕒 Última actualización: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
