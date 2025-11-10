#!/usr/bin/env bash
# shellcheck shell=bash
. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
set -euo pipefail

echo "== Git status =="
git status -s || true

echo
echo "== Divergence vs origin/main (files changed) =="
git fetch --quiet || true
git diff --name-status origin/main...HEAD || true

echo
echo "== Duplicate def names across *.py (same name in multiple files) =="
python3 - <<'PY'
import os,re,collections
pat=re.compile(r'^\s*def\s+([A-Za-z_]\w*)\s*\(',re.M)
seen=collections.defaultdict(set)
for root,_,files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            p=os.path.join(root,f)
            try:
                s=open(p,'r',errors='ignore').read()
            except Exception:
                continue
            for m in pat.finditer(s):
                seen[m.group(1)].add(p)
dups={k:v for k,v in seen.items() if len(v)>1}
for k in sorted(dups):
    print(f"{k:30s} -> " + ", ".join(sorted(dups[k])))
PY

echo
echo "== service_main.py: middleware blocks & API key checks =="
grep -n '@app.middleware("http")' service_main.py || true
grep -n 'def require_api_key_mw' service_main.py || true
# show suspect duplicate 'expected = os.getenv("API_KEY"' occurrences
nl -ba service_main.py | grep -n 'expected = os.getenv("API_KEY' || true

echo
echo "== Route includes (check for duplicates) =="
grep -n 'include_router' service_main.py || true

echo
echo "== slowapi imports anywhere =="
grep -Rn --line-number --no-messages 'slowapi' || true

echo
echo "== requirements.txt: slowapi present? =="
grep -n '^slowapi' requirements.txt || echo 'slowapi NOT listed'

echo
echo "== Entrypoint sanity =="
sed -n '1,120p' Dockerfile | nl -ba | sed -n '1,120p'
echo
echo "-- asgi.py (first 60 lines) --"
sed -n '1,60p' asgi.py | nl -ba

echo
echo "== Packaging flags (PYTHONPATH, WORKDIR/COPY) =="
grep -nE '^(ENV PYTHONPATH=|WORKDIR|COPY )' Dockerfile || true

echo
echo "== .dockerignore (make sure it doesn’t drop routes/ or *.py) =="
nl -ba .dockerignore | sed -n '1,200p'
