import json
import os
import shlex
import subprocess
from datetime import datetime

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
SERVICE_NAME = os.environ.get("NATACHA_SERVICE", "natacha-health-monitor")
REGION = os.environ.get("NATACHA_REGION", "us-central1")
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")
HOST = os.environ.get(
    "NATACHA_HOST", "natacha-health-monitor-422255208682.us-central1.run.app"
)
AUDIT_DIR = "knowledge/registry/audit"

# Alert policies de uptime ya creadas
UPTIME_POLICY_NAMES = [
    "CRun | HealthMonitor | Uptime / down",
    "CRun | HealthMonitor | Uptime / all regions down",
]


# ─────────────────────────────────────────────────────────────
def run(cmd: str) -> tuple[bool, str]:
    """Ejecuta un comando de shell y devuelve (ok, stdout). No levanta excepción."""
    try:
        out = subprocess.check_output(
            shlex.split(cmd), stderr=subprocess.STDOUT, text=True
        )
        return True, out
    except subprocess.CalledProcessError as e:
        return False, e.output


def gcloud_json(cmd: str):
    ok, out = run(cmd + " --format=json")
    if not ok or not out.strip():
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Data sources
# ─────────────────────────────────────────────────────────────
def get_service_summary():
    # Última revisión y URL del servicio
    data = gcloud_json(
        f"gcloud run services describe {SERVICE_NAME} --region {REGION} --project {PROJECT}"
    )
    if not data:
        return {}
    status = data.get("status", {})
    latest = status.get("latestReadyRevisionName")
    url = status.get("url")
    return {
        "service": SERVICE_NAME,
        "region": REGION,
        "project": PROJECT,
        "latestReadyRevision": latest,
        "url": url,
    }


def get_uptime_check():
    # Tomo el primero que matchee con el host de Cloud Run
    lst = gcloud_json(f"gcloud monitoring uptime list-configs --project {PROJECT}")
    if not lst:
        return {}
    check = None
    for item in lst:
        labels = ((item.get("monitoredResource") or {}).get("labels")) or {}
        if labels.get("host") == HOST:
            check = item
            break
    if check is None:
        # fallback: primero de la lista
        check = lst[0]
    # Describe para detalle
    name = check.get("name")
    desc = gcloud_json(f"gcloud monitoring uptime describe {name} --project {PROJECT}")
    return desc or check or {}


def get_uptime_policies():
    # Listo policies y luego describo cada una
    pols = gcloud_json(f"gcloud alpha monitoring policies list --project {PROJECT}")
    if not pols:
        return []
    picked = [p for p in pols if p.get("displayName") in UPTIME_POLICY_NAMES]
    detailed = []
    for p in picked:
        name = p.get("name")
        d = gcloud_json(
            f"gcloud alpha monitoring policies describe {name} --project {PROJECT}"
        )
        if d:
            detailed.append(d)
    return detailed


def get_open_uptime_alerts_df():
    alerts = gcloud_json(f"gcloud alpha monitoring alerts list --project {PROJECT}")
    rows = []
    if alerts:
        for a in alerts:
            policy_name = a.get("policy_name") or a.get("policy") or ""
            if policy_name in UPTIME_POLICY_NAMES:
                rows.append(
                    {
                        "policy": policy_name,
                        "condition": a.get("condition_name")
                        or a.get("condition")
                        or "-",
                        "state": a.get("state") or "-",
                        "started_at": a.get("started_at") or "-",
                        "ended_at": a.get("ended_at") or "-",
                        "id": a.get("name") or "-",
                    }
                )
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["state", "started_at"], ascending=[True, False])
    return df


def get_recent_requests_df(limit=50, freshness="10m"):
    # Logs de Cloud Run (requests)
    cmd = (
        "gcloud logging read "
        f'\'resource.type="cloud_run_revision" AND resource.labels.service_name="{SERVICE_NAME}" '
        'AND logName:"run.googleapis.com%2Frequests"\' '
        f"--project {PROJECT} --freshness={freshness} --limit={limit} --format=json"
    )
    entries = gcloud_json(cmd) or []
    rows = []
    for e in entries:
        http = e.get("httpRequest") or {}
        ts = e.get("timestamp")
        url = http.get("requestUrl")
        st = http.get("status")
        lat = e.get("latency")
        rows.append(
            {
                "timestamp": ts,
                "status": st,
                "url": url,
                "latency": lat,
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        # Orden cronológico descendente
        df = df.sort_values("timestamp", ascending=False)
    return df


def get_audit_df():
    audits = []
    if os.path.isdir(AUDIT_DIR):
        for fname in sorted(os.listdir(AUDIT_DIR)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(AUDIT_DIR, fname)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                audits.append(
                    {
                        "timestamp": data.get("timestamp"),
                        "commit_id": data.get("commit_id"),
                        "branch": data.get("branch"),
                        "status_raw": data.get("strict_check", ""),
                    }
                )
            except Exception:
                pass
    df = pd.DataFrame(audits)
    if not df.empty:
        # OK si el strict_check contiene el tilde
        df["status"] = (
            df["status_raw"]
            .astype(str)
            .apply(lambda s: "OK" if "✅" in s or "PASSED" in s else "REVIEW")
        )
        # Parseo para orden
        try:
            df["ts"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("ts", ascending=False)
        except Exception:
            pass
    return df


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Natacha | Ops Dashboard", layout="wide")
st.title("📊 Natacha — Ops Dashboard (único)")

# Header con metadata
colA, colB, colC, colD = st.columns(4)
svc = get_service_summary()
colA.metric("Service", svc.get("service", "-"))
colB.metric("Region", svc.get("region", "-"))
colC.metric("Project", svc.get("project", "-"))
colD.write(f"**URL**: {svc.get('url','-')}")

st.divider()

# ── Panel 1: Uptime Check
st.subheader("⏱ Uptime Check")
up = get_uptime_check()
if not up:
    st.warning("No se encontró uptime check.")
else:
    http = up.get("httpCheck") or {}
    mon = (up.get("monitoredResource") or {}).get("labels") or {}
    g1, g2, g3, g4 = st.columns(4)
    g1.write(f"**Path:** `{http.get('path','-')}`")
    g2.write(f"**Port:** `{http.get('port','-')}`")
    g3.write(f"**SSL:** `{http.get('useSsl','-')}`")
    g4.write(f"**Host:** `{mon.get('host','-')}`")

# ── Panel 2: Policies de Uptime
st.subheader("📣 Policies (Uptime)")
pols = get_uptime_policies()
if not pols:
    st.info("No se encontraron policies.")
else:
    rows = []
    for p in pols:
        conds = p.get("conditions") or []
        for c in conds:
            row = {
                "policy": p.get("displayName"),
                "enabled": p.get("enabled"),
                "channel": (p.get("notificationChannels") or ["-"])[0],
                "cond_name": c.get("displayName"),
                "type": (
                    "MQL" if "conditionMonitoringQueryLanguage" in c else "Threshold"
                ),
            }
            th = c.get("conditionThreshold") or {}
            if th:
                row.update(
                    {
                        "filter": th.get("filter"),
                        "duration": th.get("duration"),
                        "comparison": th.get("comparison"),
                        "thresholdValue": th.get("thresholdValue"),
                        "evaluationMissingData": th.get("evaluationMissingData"),
                    }
                )
            rows.append(row)
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

# ── Panel 3: Alertas abiertas (solo uptime)
st.subheader("🚨 Alertas de Uptime (abiertas)")
df_open = get_open_uptime_alerts_df()
if df_open.empty:
    st.success("Sin alertas de uptime abiertas.")
else:
    st.dataframe(df_open, use_container_width=True)

# ── Panel 4: Últimos requests (Cloud Run)
st.subheader("🧾 Últimos requests (10 min)")
df_req = get_recent_requests_df(limit=50, freshness="10m")
if df_req.empty:
    st.info("No hay requests recientes.")
else:
    st.dataframe(df_req, use_container_width=True)
    # Quick KPI: proporción de 5xx/4xx
    try:
        df_req["status"] = pd.to_numeric(df_req["status"], errors="coerce")
        total = len(df_req)
        err_5xx = (df_req["status"] >= 500).sum()
        err_4xx = ((df_req["status"] >= 400) & (df_req["status"] < 500)).sum()
        ok_2xx = ((df_req["status"] >= 200) & (df_req["status"] < 300)).sum()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Requests (10m)", total)
        k2.metric("2xx", ok_2xx)
        k3.metric("4xx", err_4xx)
        k4.metric("5xx", err_5xx)
    except Exception:
        pass

# ── Panel 5: Auditorías del “cerebro”
st.subheader("🧠 Auditorías del cerebro (timeline)")
df_audit = get_audit_df()
if df_audit.empty:
    st.info("No hay auditorías en knowledge/registry/audit aún.")
else:
    st.dataframe(
        df_audit[["timestamp", "branch", "commit_id", "status"]],
        use_container_width=True,
    )
    try:
        # Serie binaria para chart
        series = df_audit.copy()
        series["ok"] = series["status"].map({"OK": 1, "REVIEW": 0})
        series = series.set_index("ts")["ok"].sort_index()
        st.line_chart(series)
    except Exception:
        pass

st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
