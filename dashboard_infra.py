import json
import os
import time

import requests
import streamlit as st

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Infraestructura Natacha", page_icon="🌐", layout="wide")


def load_data():
    path = os.path.expanduser("~/Projects/natacha-api/infra_status.json")
    if not os.path.exists(path):
        st.error("❌ No se encontró el archivo infra_status.json.")
        return None
    with open(path, "r") as f:
        return json.load(f)


def check_url_health(url: str) -> str:
    """Devuelve el estado de salud del servicio."""
    try:
        r = requests.get(url, timeout=3)
        if r.status_code < 400:
            return "✅"
        else:
            return "⚠️"
    except Exception:
        return "❌"


# === TÍTULO ===
st.title("🌐 Monitoreo de Infraestructura Natacha")
st.caption("Panel avanzado de estado en tiempo real - Proyecto asistente-sebastian")

data = load_data()
if not data:
    st.stop()

# === SECCIÓN: RESUMEN GENERAL ===
st.header("📊 Estado General del Sistema")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🕒 Última actualización", data["timestamp"])
col2.metric("☁️ Proyecto", data["project"])
col3.metric("💻 VM", data["vm_status"])
col4.metric("💾 Uso de disco", data["disk_usage"])

# Estado general del sistema
if data["vm_status"] == "RUNNING":
    st.success("💚 VM activa y operativa")
else:
    st.error("❌ VM detenida o no responde")

st.divider()

# === SECCIÓN: DOCKER ===
st.subheader("🐳 Contenedores Docker")
docker_data = data.get("docker_containers", [])
if not docker_data:
    st.warning("No se encontraron contenedores activos.")
else:
    for c in docker_data:
        status = c["status"].lower()
        color = "✅" if "up" in status else "⚠️" if "restarting" in status else "❌"
        st.markdown(f"{color} **{c['name']}** — {c['status']} — `{c['ports']}`")

st.divider()

# === SECCIÓN: CLOUD RUN ===
st.subheader("🚀 Servicios Cloud Run")
cloud_run = data.get("cloud_run_services", [])
if not cloud_run:
    st.warning("No se encontraron servicios Cloud Run.")
else:
    cols = st.columns(2)
    for i, s in enumerate(cloud_run):
        url = s.get("status", {}).get("url", "")
        if not url:
            continue
        health = check_url_health(url)
        cols[i % 2].markdown(f"{health} [{url}]({url})")

st.divider()

# === AUTO REFRESH ===
refresh_sec = st.slider("⏱️ Actualizar cada (segundos)", 10, 300, 60)
st.caption(
    "El panel se actualizará automáticamente con los últimos datos de `check_infra_status.sh`."
)
time.sleep(refresh_sec)
st.experimental_rerun()
