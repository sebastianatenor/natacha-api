import os, sys, json, subprocess, re, pathlib, argparse

PROJECT      = os.environ.get("PROJECT", "asistente-sebastian")
REGION       = os.environ.get("REGION", "us-central1")
SVC          = os.environ.get("SVC", "natacha-api")
PROJECT_NUM  = os.environ.get("PROJECT_NUM", "422255208682")
REG_PATH     = "REGISTRY.md"
CANONICAL    = f"https://{SVC}-{PROJECT_NUM}.{REGION}.run.app"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if r.returncode != 0:
        print(r.stderr.strip())
        sys.exit(1)
    return r.stdout.strip()

def get_cloud_run_facts():
    url = sh(f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} --format='value(status.url)'")
    rev = sh(f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} --format='value(status.latestReadyRevisionName)'")
    sa  = sh(f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} --format='value(spec.template.spec.serviceAccountName)'")
    # Intentar detectar nombre del secreto montado en env
    raw = sh(f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} --format=json")
    secret = None
    try:
        data = json.loads(raw)
        envs = data["spec"]["template"]["spec"]["containers"][0].get("env", [])
        for e in envs:
            if e.get("name") == "API_KEY" and "valueFrom" in e:
                sk = e["valueFrom"].get("secretKeyRef") or {}
                secret = sk.get("name")
                break
    except Exception:
        secret = None
    return {"status_url": url, "latest_rev": rev, "service_account": sa, "secret": secret or "NATACHA_API_KEY"}

def ensure_registry_fields(url, rev, sa, secret):
    if not pathlib.Path(REG_PATH).exists():
        # Crear plantilla mínima si no existe
        pathlib.Path(REG_PATH).write_text("# 🧭 REGISTRY – Proyecto Natacha\n\n- URL: \n- Revisión: \n- Service Account: \n- Secret montado: \n", encoding="utf-8")
    txt = pathlib.Path(REG_PATH).read_text(encoding="utf-8")
    def rep(label, value):
        pattern = rf"^- {re.escape(label)}:.*$"
        repl = f"- {label}: {value}"
        if re.search(pattern, txt, flags=re.MULTILINE):
            return re.sub(pattern, repl, txt, flags=re.MULTILINE)
        else:
            # si no está, lo agregamos al inicio
            return repl + "\n" + txt
    txt = rep("URL", url)
    txt = rep("Revisión", rev)
    txt = rep("Service Account", sa)
    txt = rep("Secret montado", secret)
    pathlib.Path(REG_PATH).write_text(txt, encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-fix", action="store_true")
    args = ap.parse_args()

    facts = get_cloud_run_facts()

    print("== Cloud Run (real) ==")
    print(f"- URL: {facts['status_url']}")
    print(f"- Revisión: {facts['latest_rev']}")
    print(f"- Service Account: {facts['service_account']}")
    print(f"- Secret montado: {facts['secret']}")

    ok = facts["status_url"] in {CANONICAL}
    if not ok:
        print(f"ℹ️  Usaremos la canónica: {CANONICAL}")

    if args.auto_fix:
        ensure_registry_fields(CANONICAL, facts["latest_rev"], facts["service_account"], facts["secret"])
        print("✅ REGISTRY.md actualizado con URL canónica y metadatos actuales.")

if __name__ == "__main__":
    main()
