import json
from typing import List, Dict, Any
import os

import google.auth
from google.auth.transport.requests import AuthorizedSession


def _get_auth_session() -> AuthorizedSession:
    """Crea una sesión autenticada usando ADC (Workload Identity / SA del servicio)."""
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(creds)


def _list_services(project: str, region: str) -> List[Dict[str, Any]]:
    """
    Llama a la API de Cloud Run v2 para listar servicios (maneja paginación).
    GET https://run.googleapis.com/v2/projects/{project}/locations/{region}/services
    """
    session = _get_auth_session()
    base = f"https://run.googleapis.com/v2/projects/{project}/locations/{region}/services"
    services: List[Dict[str, Any]] = []

    url = base
    params = {"pageSize": 100}
    while True:
        resp = session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json() or {}
        batch = data.get("services", [])
        services.extend(batch)
        token = data.get("nextPageToken")
        if not token:
            break
        params["pageToken"] = token

    return services


def _parse_conditions(svc: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve estado legible y ‘healthy’ a partir de las condiciones."""
    url = svc.get("uri") or (svc.get("status", {}) or {}).get("url", "N/A")
    traffic = svc.get("traffic") or (svc.get("status", {}) or {}).get("traffic", []) or []
    full_name = svc.get("name", "unknown")
    name = full_name.split("/")[-1] if "/" in full_name else full_name
    conditions = svc.get("conditions") or (svc.get("status", {}) or {}).get("conditions", []) or []

    cond_map = {str(c.get("type", "")).lower(): c for c in conditions if isinstance(c, dict)}
    ready = cond_map.get("ready") or cond_map.get("readycondition")
    routes_ready = cond_map.get("routesready") or cond_map.get("route-ready") or cond_map.get("routesreadycondition")

    def _fmt(c):
        if not c:
            return "unknown: unknown (no conditions)"
        ctype = c.get("type", "Unknown")
        cstatus = str(c.get("status", "Unknown")).lower()
        msg = c.get("message") or c.get("reason") or "N/A"
        return f"{ctype.lower()}: {cstatus} ({msg})"

    display = _fmt(ready) if ready else (_fmt(routes_ready) if routes_ready else _fmt(None))
    healthy = (
        (ready and str(ready.get("status", "")).lower() in ("true", "ok", "ready", "success")) or
        (routes_ready and str(routes_ready.get("status", "")).lower() in ("true", "ok", "ready", "success"))
    )

    return {"name": name, "url": url or "N/A", "status": display, "traffic": traffic, "healthy": healthy}


def get_cloud_run_services(project: str = None, region: str = None) -> List[Dict[str, Any]]:
    """
    Lista servicios Cloud Run vía API v2 (sin gcloud).
    Usa env GCP_PROJECT/GCP_REGION si están, sino defaults del proyecto.
    """
    project = project or os.environ.get("GCP_PROJECT") or "asistente-sebastian"
    region = region or os.environ.get("GCP_REGION") or "us-central1"
    try:
        raw = _list_services(project, region)
        parsed: List[Dict[str, Any]] = []
        for s in raw:
            info = _parse_conditions(s)
            status_str = info.get("status", "").lower()
            if "healthcheckcontainererror" in status_str or "failed" in status_str:
                print(f"🚫 Servicio omitido (fallido): {info['name']}")
                continue
            if "deleted" in status_str:
                print(f"🗑️ Servicio eliminado: {info['name']}")
                continue
            parsed.append(info)
        print(f"✅ {len(parsed)} servicios activos encontrados.")
        return parsed
    except Exception as e:
        print(f"🚨 Error inesperado al obtener servicios Cloud Run: {e}")
        return []
