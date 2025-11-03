import os
import platform
import socket
import subprocess
from datetime import datetime

import pandas as pd
import psutil
import streamlit as st


def show():
    st.title("🖥️ Sistema Local — Estado del Host")
    st.caption("Información del entorno y recursos físicos")

    # --- Información del sistema
    uname = platform.uname()
    st.subheader("📦 Información del sistema operativo")
    st.write(
        {
            "Sistema": uname.system,
            "Versión": uname.version,
            "Release": uname.release,
            "Arquitectura": uname.machine,
            "Procesador": uname.processor,
            "Python": platform.python_version(),
            "Usuario": os.getenv("USER"),
        }
    )

    # --- Recursos principales
    st.subheader("⚙️ Recursos del sistema")
    col1, col2, col3 = st.columns(3)
    col1.metric("CPU", f"{psutil.cpu_percent()}%")
    col2.metric("RAM", f"{psutil.virtual_memory().percent}%")
    col3.metric("Disco", f"{psutil.disk_usage('/').percent}%")

    # --- Red
    st.subheader("🌐 Red")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        st.write(f"🖧 Hostname: `{hostname}` — IP local: `{local_ip}`")
    except Exception as e:
        st.warning(f"No se pudo obtener la IP local: {e}")

    st.write("### Interfaces de red")
    net = psutil.net_if_addrs()
    for iface, addrs in net.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                st.write(f"🔹 `{iface}` → {addr.address}")

    # --- Procesos activos
    st.subheader("🧩 Procesos activos")
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        procs.append(p.info)
    df = pd.DataFrame(procs).sort_values("cpu_percent", ascending=False).head(10)
    st.dataframe(df, use_container_width=True)

    # --- Puertos abiertos
    st.subheader("🔌 Puertos abiertos")
    try:
        cmd = ["lsof", "-i", "-P", "-n"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = [l for l in result.stdout.splitlines() if ":" in l]
        st.text_area("Puertos activos", "\n".join(lines[:30]), height=200)
    except Exception as e:
        st.warning(f"No se pudieron listar los puertos: {e}")

    st.caption(
        f"Última actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
