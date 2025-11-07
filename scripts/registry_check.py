import json, os, subprocess, sys

PROJECT = os.environ.get("PROJECT", "asistente-sebastian")
REGION  = os.environ.get("REGION", "us-central1")
SVC     = os.environ.get("SVC", "natacha-api")
PROJECT_NUM = os.environ.get("PROJECT_NUM", "422255208682")  # mantenemos explícito

REG_PATH = "REGISTRY.md"

def sh(cmd):
    r = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if r.returncode != 0:
        print(r.stderr.strip())
        sys.exit(1)
    return r.stdout.strip()

def parse_registry_md(path):
    url = rev = sa = secret = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("- URL:"):
                url = line.split(":",1)[1].strip()
            elif line.startswith("- Revisión:"):
                rev = line.split(":",1)[1].strip()
            elif line.startswith("- Service Account:"):
                sa = line.split(":",1)[1].strip()
            elif line.startswith("- Secret montado:"):
                secret = line.split(":",1)[1].strip()
    return {"url": url, "rev": rev, "sa": sa, "secret": secret}

def get_cloud_run_facts():
    # status.url (legacy/hashed)
    cloud_url = sh(
        f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} "
        f"--format='value(status.url)'"
    )
    # latest ready revision
    latest_rev = sh(
        f"gcloud run services describe {SVC} --project {PROJECT} --region {REGION} "
        f"--format='value(status.latestReadyRevisionName)'"
    )
    return {"cloud_url": cloud_url, "latest_rev": latest_rev}

def whoami(url):
    try:
        out = sh(f"curl -sS {url}/__whoami")
        return json.loads(out)
    except Exception:
        return {}

def main():
    reg = parse_registry_md(REG_PATH)
    facts = get_cloud_run_facts()
    canonical = f"https://{SVC}-{PROJECT_NUM}.{REGION}.run.app"

    print("== REGISTRY.md ==")
    print(f"- URL: {reg['url']}")
    print(f"- Revisión: {reg['rev']}")
    print(f"- Service Account: {reg['sa']}")
    print(f"- Secret montado: {reg['secret']}\n")

    print("== Cloud Run (real) ==")
    print(f"- URL (status.url): {facts['cloud_url']}")
    print(f"- Revisión: {facts['latest_rev']}")

    # Criterio de URL válida: coincide con status.url O con la canónica numérica
    ok_url = reg["url"] in {facts["cloud_url"], canonical}
    if not ok_url:
        print(f"❌ URL en REGISTRY.md NO coincide (aceptado: status.url o {canonical})")
    else:
        print("✅ URL aceptada (status.url o canónica numérica)")

    # whoami rápido contra la canónica (preferida)
    w = whoami(canonical)
    if w:
        print(f"🟢 whoami (canónica): module={w.get('module')}, routes={w.get('routes_count')}")
    else:
        print("⚠️ whoami en canónica no respondió")

    if ok_url:
        print("\n✅ Todo OK (URLs en sync bajo criterio canónico)")
    else:
        print("\n⚠️ Diferencias / fallos detectados")

if __name__ == "__main__":
    import argparse, re, pathlib, subprocess, json

    ap = argparse.ArgumentParser()
    ap.add_argument("--auto-fix", action="store_true", help="Actualizar REGISTRY.md automáticamente")
    args = ap.parse_args()

    # === 1️⃣ Obtener datos actuales desde gcloud ===
    svc = "natacha-api"
    proj = "asistente-sebastian"
    reg = "us-central1"

    def gval(fmt):
        try:
            return subprocess.check_output([
                "gcloud", "run", "services", "describe", svc,
                "--project", proj, "--region", reg,
                "--format", fmt
            ], text=True).strip()
        except subprocess.CalledProcessError:
            return "N/A"

    url = gval("value(status.url)")
    rev = gval("value(status.latestReadyRevisionName)")
    sa = gval("value(spec.template.spec.serviceAccountName)")

    try:
        js = subprocess.check_output([
            "gcloud", "run", "services", "describe", svc,
            "--project", proj, "--region", reg,
            "--format=json"
        ], text=True)
        data = json.loads(js)
        secret_name = next(
            (e["valueFrom"]["secretKeyRef"]["name"]
             for e in data["spec"]["template"]["spec"]["containers"][0]["env"]
             if e["name"] == "API_KEY"),
            "NATACHA_API_KEY"
        )
    except Exception:
        secret_name = "NATACHA_API_KEY"

    print("== Cloud Run (real) ==")
    print(f"- URL: {url}")
    print(f"- Revisión: {rev}")
    print(f"- Service Account: {sa}")
    print(f"- Secret montado: {secret_name}")

    # === 2️⃣ Si se pasa --auto-fix, actualizar REGISTRY.md ===
    if args.auto_fix:
        path = pathlib.Path("REGISTRY.md")
        txt = path.read_text(encoding="utf-8")

        def rep(label, value):
            pattern = rf"^- {re.escape(label)}:.*$"
            repl = f"- {label}: {value}"
            return re.sub(pattern, repl, txt, flags=re.MULTILINE)

        txt = rep("URL", url)
        txt = rep("Revisión", rev)
        txt = rep("Service Account", sa)
        txt = rep("Secret montado", secret_name or "NATACHA_API_KEY")

        path.write_text(txt, encoding="utf-8")
        print("✅ REGISTRY.md actualizado automáticamente.")
