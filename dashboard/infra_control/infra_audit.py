import json
import os

import pandas as pd
import streamlit as st

AUDIT_DIR = "knowledge/registry/audit"
DOCKER_DIR = "logs"


def _list_audit_files():
    files = []
    if os.path.isdir(AUDIT_DIR):
        for f in os.listdir(AUDIT_DIR):
            if f.endswith(".json") or f.endswith(".txt"):
                path = os.path.join(AUDIT_DIR, f)
                files.append(
                    {
                        "file": f,
                        "path": path,
                        "type": "json" if f.endswith(".json") else "text",
                        "size": os.path.getsize(path),
                    }
                )
    if os.path.isdir(DOCKER_DIR):
        for f in os.listdir(DOCKER_DIR):
            if f.startswith("docker_"):
                path = os.path.join(DOCKER_DIR, f)
                files.append(
                    {
                        "file": f,
                        "path": path,
                        "type": "text",
                        "size": os.path.getsize(path),
                    }
                )
    files.sort(key=lambda x: x["file"], reverse=True)
    return files


def _load_file(item: dict):
    path = item["path"]
    # 1) intento json
    if item["type"] == "json":
        try:
            with open(path, "r") as f:
                return {"mode": "json", "data": json.load(f)}
        except Exception:
            # no es json real → lo devuelvo como texto
            with open(path, "r") as f:
                return {"mode": "text", "raw": f.read()}
    else:
        with open(path, "r") as f:
            return {"mode": "text", "raw": f.read()}


def show():
    st.subheader("🧩 Auditoría Global de Infraestructura")
    st.caption("Últimas corridas de auditoría sobre REGISTRY / servicios / duplicados")

    files = _list_audit_files()
    if not files:
        st.info("No se encontraron auditorías en disco.")
        return

    df = pd.DataFrame(
        [{"Archivo": f["file"], "Tipo": f["type"], "Tamaño": f["size"]} for f in files]
    )
    st.dataframe(df, use_container_width=True)

    pick_names = [f["file"] for f in files]
    picked = st.selectbox("Ver detalle de una auditoría", pick_names, index=0)
    current = next((f for f in files if f["file"] == picked), None)
    if not current:
        return

    loaded = _load_file(current)

    st.markdown("#### Detalle")
    if loaded["mode"] == "json":
        data = loaded["data"]
        if isinstance(data, dict):
            main_keys = [
                "timestamp",
                "summary",
                "service",
                "result",
                "duplicates",
                "alerts",
            ]
            cols = st.columns(len(main_keys))
            for i, k in enumerate(main_keys):
                val = data.get(k)
                if val is None:
                    continue
                if isinstance(val, (list, dict)):
                    cols[i].metric(k, f"{len(val)} item(s)")
                else:
                    cols[i].metric(k, str(val))
            with st.expander("📄 Ver JSON completo"):
                st.json(data)
        else:
            # json pero no es dict
            with st.expander("📄 Ver contenido JSON"):
                st.write(data)
    else:
        # texto plano (lo que te estaba rompiendo)
        with st.expander("📝 Salida completa del comando (raw)", expanded=True):
            st.code(loaded["raw"])
