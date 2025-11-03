import os
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

# Fuente 1: monitor de infraestructura (health-monitor en Cloud Run)
INFRA_URL = os.getenv(
    "NATACHA_HEALTH_URL",
    "https://natacha-health-monitor-422255208682.us-central1.run.app",
)

# Fuente 2: modo operativo (tareas/memorias) desde Natacha API
OPS_URL = os.getenv(
    "NATACHA_CONTEXT_API", "https://natacha-api-422255208682.us-central1.run.app"
)


def _fetch_infra_history():
    try:
        r = requests.get(f"{INFRA_URL}/infra_history_cloud", timeout=8)
        if r.status_code == 200:
            data = r.json()
            # el monitor a veces devuelve {"status":"ok","count":0,"data":[]}
            if isinstance(data, dict):
                return data.get("data") or []
            return data or []
    except Exception:
        return []
    return []


def _fetch_ops_dashboard():
    """Trae /dashboard/data de Natacha API para mostrar tareas si no hay infra."""
    try:
        r = requests.get(f"{OPS_URL}/dashboard/data", timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def main():
    st.header("🩺 Panel de Salud del Sistema Natacha")
    st.caption(
        "Monitoreo en tiempo real desde infraestructura 👉 si no hay registros, muestra el estado operativo."
    )

    infra = _fetch_infra_history()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.write(f"🕒 Última actualización: {now_utc}")

    if infra:
        # ======== MODO INFRA ========
        st.success("🟢 Monitor de infraestructura ONLINE y con registros.")
        df = pd.DataFrame(infra)
        # aseguramos timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.sort_values("timestamp", ascending=False)
            last = df.iloc[0]
            st.markdown(f"**Último diagnóstico:** {last.get('timestamp')}")
            st.markdown(f"**Entorno:** `{last.get('environment','-')}`")
            disk = last.get("disk_usage") or "-"
            st.markdown(f"**Uso de disco:** `{disk}`")
        st.subheader("📋 Últimos diagnósticos")
        st.dataframe(df, width="stretch")
        return

    # ======== MODO OPERATIVO (FALLBACK) ========
    st.info("🛠️ Monitor de infraestructura ONLINE pero sin registros todavía.")
    st.caption(
        "Esto pasa cuando el servicio de health se desplegó pero todavía no escribió en Firestore."
    )
    st.markdown("—")

    data = _fetch_ops_dashboard()
    if not data:
        st.error("❌ No se pudo obtener tampoco el estado operativo desde Natacha API.")
        return

    st.subheader("💼 Modo OPERATIVO (proyectos / tareas) — datos desde Natacha API")
    totals = data.get("totals") or {}
    st.write(
        f"**Proyectos**: {totals.get('projects', 0)} | **Tareas**: {totals.get('tasks', 0)} | **Memorias**: {totals.get('memories', 0)}"
    )

    projects = data.get("projects") or []
    if not projects:
        st.warning("No hay proyectos/tareas guardados todavía.")
        return

    # vista linda en texto
    for p in projects:
        name = p.get("name", "sin-nombre")
        pending = p.get("pending_tasks", 0)
        st.write(f"• **{name}** — {pending} pendiente(s)")
        urgent = p.get("urgent_title") or (p.get("urgent_task") or {}).get("title")
        urgent_due = p.get("urgent_due") or (p.get("urgent_task") or {}).get("due")
        if urgent:
            st.write(
                f"  Urgente: {urgent}"
                + (f" | vence: {urgent_due}" if urgent_due else "")
            )
        alerts = p.get("alerts") or []
        if alerts:
            st.write("  " + " | ".join(f"⚠️ {a}" for a in alerts))

    # tabla solo si hay más de 3
    if len(projects) > 3:
        dfp = []
        for p in projects:
            dfp.append(
                {
                    "project": p.get("name", ""),
                    "pending_tasks": p.get("pending_tasks", 0),
                    "urgent_title": p.get("urgent_title")
                    or (p.get("urgent_task") or {}).get("title")
                    or "",
                    "urgent_due": p.get("urgent_due")
                    or (p.get("urgent_task") or {}).get("due")
                    or "",
                }
            )
        st.dataframe(pd.DataFrame(dfp), width="stretch")
