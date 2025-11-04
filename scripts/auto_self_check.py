import json
import subprocess
import datetime
from pathlib import Path
import requests

CLOUD_URL = "https://natacha-api-422255208682.us-central1.run.app"
REGISTRY = Path("REGISTRY.md")
REPORT = Path("infra_status_auto.json")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip()}"

def check_cloud_run():
    info = run_cmd([
        "gcloud", "run", "services", "describe", "natacha-api",
        "--platform", "managed",
        "--region", "us-central1",
        "--format", "json"
    ])
    try:
        data = json.loads(info)
        rev = data.get("status", {}).get("latestCreatedRevisionName")
        url = data.get("status", {}).get("url")
        return {"revision": rev, "url": url, "status": "ok"}
    except Exception:
        return {"status": "error", "raw": info}

def check_registry():
    if not REGISTRY.exists():
        return {"status": "missing"}
    text = REGISTRY.read_text(encoding="utf-8")
    return {
        "status": "ok",
        "length": len(text.splitlines()),
        "contains_cloud_run": "natacha-api" in text,
    }

def ping_system_status():
    try:
        r = requests.get(f"{CLOUD_URL}/system/status", timeout=10)
        return {"status_code": r.status_code, "json": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def list_repo_remote():
    try:
        r = requests.get(f"{CLOUD_URL}/auto/list_repo", timeout=15)
        if r.status_code == 200:
            items = r.json().get("items", [])
            return {"status": "ok", "count": len(items)}
        return {"status": "fail", "code": r.status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def upsert_memory(summary, detail):
    try:
        payload = {"summary": summary, "detail": detail, "project": "auto_self_check"}
        requests.post(f"{CLOUD_URL}/memory/upsert", json=payload, timeout=10)
    except Exception:
        pass  # silencioso, no bloqueante

def main():
    now = datetime.datetime.utcnow().isoformat()
    report = {
        "timestamp": now,
        "checks": {
            "cloud_run": check_cloud_run(),
            "registry": check_registry(),
            "system_status": ping_system_status(),
            "repo": list_repo_remote(),
        },
    }

    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"✅ Reporte generado en {REPORT}")
    upsert_memory("Auto self-check report", json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
