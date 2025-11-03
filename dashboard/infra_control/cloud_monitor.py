import json
import os
import subprocess

import pandas as pd
import streamlit as st

PROJECT = os.getenv("GCP_PROJECT", "asistente-sebastian")
REGION = os.getenv("NATACHA_REGION", "us-central1")


def run(cmd: str):
    try:
        out = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.STDOUT
        )
        return out, None
    except subprocess.CalledProcessError as e:
        return e.output, e


def list_cloud_run():
    cmd = (
        f"gcloud run services list --project={PROJECT} --region={REGION} --format=json"
    )
    out, err = run(cmd)
    if err:
        return []
    try:
        return json.loads(out)
    except Exception:
        return []


def show():
    st.subheader("☁️ Servicios Cloud Run")
    st.caption(f"Proyecto: `{PROJECT}` | Región: `{REGION}`")

    services = list_cloud_run()
    if not services:
        st.warning(
            "No se pudieron obtener los servicios de Cloud Run (¿falta gcloud o permisos?)."
        )
        return

    rows = []
    for s in services:
        rows.append(
            {
                "Servicio": s.get("metadata", {}).get("name", ""),
                "URL": s.get("status", {}).get("url", ""),
                "Última revisión": s.get("status", {}).get(
                    "latestReadyRevisionName", ""
                ),
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    # mini semáforo
    ok = [r for r in rows if r["URL"]]
    st.success(f"✅ {len(ok)}/{len(rows)} servicios con URL pública")
