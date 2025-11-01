import os
import platform
import psutil
import streamlit as st
import pandas as pd

def get_system_info():
    return {
        "Sistema": platform.system(),
        "Versión": platform.version(),
        "Release": platform.release(),
        "Arquitectura": platform.machine(),
        "Procesador": platform.processor(),
        "Python": platform.python_version(),
        "Usuario": os.getenv("USER") or os.getenv("USERNAME") or "N/A",
    }

def get_usage_info():
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, mem, disk
    except Exception:
        return 0, 0, 0

def get_top_processes(limit=5):
    rows = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = p.info
            info['cpu_percent'] = info.get('cpu_percent') or 0.0
            info['memory_percent'] = info.get('memory_percent') or 0.0
            rows.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    rows = sorted(rows, key=lambda x: x['cpu_percent'], reverse=True)
    return rows[:limit]

def show():
    st.subheader("📦 Información del sistema operativo")

    info = get_system_info()
    cpu, mem, disk = get_usage_info()

    col1, col2, col3 = st.columns(3)
    col1.metric("⚙️ CPU %", f"{cpu:.1f}%")
    col2.metric("💾 RAM usada", f"{mem:.1f}%")
    col3.metric("📀 Disco usado", f"{disk:.1f}%")

    st.markdown("### 🧠 Detalle del sistema")
    st.table(pd.DataFrame(info.items(), columns=["Campo", "Valor"]))

    st.markdown("---")
    st.subheader("🔎 Procesos con mayor uso de CPU")
    procs = get_top_processes()
    if procs:
        st.dataframe(pd.DataFrame(procs), use_container_width=True)
    else:
        st.info("No se pudieron obtener procesos activos.")
