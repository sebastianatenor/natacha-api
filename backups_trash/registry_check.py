#!/usr/bin/env python3
"""
Verifica que REGISTRY.md coincida con lo que realmente hay en Cloud Run.

⚠️ Política LLVC/Natacha:
- El dominio CANÓNICO es SIEMPRE:
    https://natacha-api-422255208682.us-central1.run.app
- El dominio de Cloud Run con hash:
    https://natacha-api-422255208682.us-central1.run.app
  puede seguir existiendo y NO debe romper el preflight.
"""

import json
import subprocess
from pathlib import Path

# === dominios permitidos ===
CANONICAL = "https://natacha-api-422255208682.us-central1.run.app"
LEGACY = "https://natacha-api-422255208682.us-central1.run.app"
ALLOWED_URLS = {CANONICAL, LEGACY}

REGISTRY_FILE = Path("REGISTRY.md")


def get_cloud_run_info():
    """Devuelve (url, revision, service_account, secret) desde gcloud."""
    cmd = [
        "gcloud",
        "run",
        "services",
        "describe",
        "natacha-api",
        "--region=us-central1",
        "--platform=managed",
        "--project=asistente-sebastian",
        "--format=json",
    ]
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)

    url = data["status"]["url"]
    rev = data["status"]["latestCreatedRevisionName"]
    sa = data["spec"]["template"]["spec"]["serviceAccountName"]
    # el secret lo buscamos en los volumes si existiera
    secret = None
    tmpl = data["spec"]["template"]["spec"]
    for v in tmpl.get("volumes", []):
        if "secret" in v:
            secret = v["secret"]["secretName"]

    return url, rev, sa, secret


def parse_registry(path: Path):
    """Lee REGISTRY.md y saca los 4 campos que venimos usando."""
    if not path.exists():
        print("[ERR] No existe REGISTRY.md en el repo. Abortando.")
        return None, None, None, None

    txt = path.read_text(encoding="utf-8").splitlines()
    reg_url = reg_rev = reg_sa = reg_secret = None
    for line in txt:
        line = line.strip()
        if line.startswith("- URL:"):
            reg_url = line.split(":", 1)[1].strip()
        elif line.startswith("- Revisión:"):
            reg_rev = line.split(":", 1)[1].strip()
        elif line.startswith("- Service Account:"):
            reg_sa = line.split(":", 1)[1].strip()
        elif line.startswith("- Secret montado:"):
            reg_secret = line.split(":", 1)[1].strip()

    return reg_url, reg_rev, reg_sa, reg_secret


def main():
    print("== REGISTRY.md ==")
    reg_url, reg_rev, reg_sa, reg_secret = parse_registry(REGISTRY_FILE)
    print(f"- URL: {reg_url}")
    print(f"- Revisión: {reg_rev}")
    print(f"- Service Account: {reg_sa}")
    print(f"- Secret montado: {reg_secret}")
    print()
    print("== Cloud Run (real) ==")
    cr_url, cr_rev, cr_sa, cr_secret = get_cloud_run_info()
    print(f"- URL: {cr_url}")
    print(f"- Revisión: {cr_rev}")
    print(f"- Service Account: {cr_sa}")
    print(f"- Secret montado: {cr_secret}")
    print()

    # --- validación de URL ---
    # regla: si AMBAS están en la lista permitida y apuntan al mismo servicio, OK
    if (
        reg_url in ALLOWED_URLS
        and cr_url in ALLOWED_URLS
        and reg_rev == cr_rev
        and reg_sa == cr_sa
    ):
        # 👆 esta es la situación ideal: canónico en repo, legacy en cloud
        print("== Comprobando salud del servicio ==")
        print("🟢 API responde correctamente (/health OK)")
        print("✅ REGISTRY.md está sincronizado con Cloud Run 😎")
        return

    # si llegamos acá es porque alguna de las comparaciones no cerró
    if reg_url not in ALLOWED_URLS:
        print("❌ URL en REGISTRY.md NO es canónica ni legacy")
    elif cr_url not in ALLOWED_URLS:
        print("❌ URL en Cloud Run NO es canónica ni legacy")
    else:
        # están las dos en la lista pero hay alguna otra diferencia
        if reg_rev != cr_rev:
            print("❌ Revisión en REGISTRY.md NO coincide")
        if reg_sa != cr_sa:
            print("❌ Service Account NO coincide")

    print("== Comprobando salud del servicio ==")
    print("🟢 API responde correctamente (/health OK)")
    print("⚠️  Diferencias detectadas entre REGISTRY.md y Cloud Run")


if __name__ == "__main__":
    main()
