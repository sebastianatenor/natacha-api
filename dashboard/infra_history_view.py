import os
import json
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# 🔹 Importamos acceso local y cloud
from health_monitor.infra_local_history import get_history
from health_monitor.infra_sync import pull_from_firestore

router = APIRouter()

def _format_entry(entry: dict, idx: int) -> str:
    """Formatea una entrada de historial como una fila HTML."""
    ts = entry.get("timestamp", "—")
    env = entry.get("environment", "—")
    disk = entry.get("disk_usage", "—")
    vm_count = len(entry.get("vm_status", [])) if entry.get("vm_status") else 0
    docker_count = len(entry.get("docker_containers", [])) if entry.get("docker_containers") else 0
    cloud_count = len(entry.get("cloud_run_services", [])) if entry.get("cloud_run_services") else 0

    return f"""
    <tr>
        <td>{idx}</td>
        <td>{ts}</td>
        <td>{env}</td>
        <td>{vm_count}</td>
        <td>{docker_count}</td>
        <td>{cloud_count}</td>
        <td>{disk}</td>
    </tr>
    """


@router.get("/infra_dashboard", response_class=HTMLResponse)
def infra_dashboard_view():
    """Dashboard visual para el historial de infraestructura."""
    # 🔸 Intentar traer Firestore, fallback a local
    try:
        entries = pull_from_firestore()
        if isinstance(entries, dict) and "status" in entries and entries["status"] == "error":
            raise Exception(entries["detail"])
    except Exception:
        entries = get_history()

    rows = "".join([_format_entry(e, i + 1) for i, e in enumerate(entries)]) if entries else "<tr><td colspan=7>No hay registros</td></tr>"

    html = f"""
    <html>
    <head>
        <title>Natacha Infra Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #111;
                color: #eee;
                margin: 40px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #333;
                padding: 8px 12px;
                text-align: center;
            }}
            th {{
                background-color: #222;
            }}
            tr:nth-child(even) {{
                background-color: #1a1a1a;
            }}
            h1 {{
                text-align: center;
                color: #00ffc3;
            }}
            .source {{
                text-align: right;
                font-size: 0.9em;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <h1>🧠 Natacha Infrastructure Dashboard</h1>
        <div class="source">Fuente: Firestore (si disponible) o Local</div>
        <table>
            <tr>
                <th>#</th>
                <th>Timestamp</th>
                <th>Ambiente</th>
                <th>VMs</th>
                <th>Docker</th>
                <th>CloudRun</th>
                <th>Uso Disco</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
