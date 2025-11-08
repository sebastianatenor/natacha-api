#!/usr/bin/env bash
set -euo pipefail

PROJ="${PROJ:-$(gcloud config get-value core/project 2>/dev/null || true)}"
REG="${REG:-$(gcloud config get-value run/region 2>/dev/null || echo us-central1)}"
SVC="${SVC:-natacha-api}"

CANON="${NATACHA_CONTEXT_API:-$(gcloud run services describe "$SVC" --project "$PROJ" --region "$REG" --format='value(status.url)' 2>/dev/null || true)}"

# Rutas seguras (NO tocamos backups/.git/infra_snapshots/SNAPSHOTS)
targets=(
  "scripts/*.sh" "scripts/*.py"
  "legacy/**/*.py" "legacy/**/*.sh"
  "system/**/*.py"
)
# Patrones a reemplazar
pat1='https://natacha-api-422255208682.us-central1.run.app'
pat2='https://natacha-api-mkwskljrhq-uc.a.run.app'

changed=0
for gl in "${targets[@]}"; do
  for f in $(bash -lc "shopt -s globstar nullglob; echo $gl"); do
    [ -f "$f" ] || continue
    # saltar binarios
    file "$f" | grep -qi 'text' || continue
    cp "$f" "$f.bak.ncanon"
    # shell: export CANONICAL
    if [[ "$f" == *.sh ]]; then
      awk -v canon="$CANON" -v p1="$pat1" -v p2="$pat2" '
        BEGIN{replaced=0}
        {
          gsub(p1, "${CANONICAL}", $0); gsub(p2, "${CANONICAL}", $0);
          print $0
        }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
      # inyectar bloque CANONICAL si no existe
      grep -q 'CANONICAL=' "$f" || sed -i '1i CANONICAL="${NATACHA_CONTEXT_API:-'"$CANON"'}"' "$f"
      changed=$((changed+1))
    fi
    # python: usar os.getenv('NATACHA_CONTEXT_API', '<live>')
    if [[ "$f" == *.py ]]; then
      python3 - "$f" <<PY
import os, sys, re, pathlib
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
pat1 = r"$pat1"; pat2 = r"$pat2"
canon = os.environ.get("CANON","$CANON")
env_expr = f"os.getenv('NATACHA_CONTEXT_API', '{canon}')"
s2 = s.replace(pat1, env_expr).replace(pat2, env_expr)
if s2 != s:
    if not re.search(r'^\s*import\s+os\b', s2, re.M):
        s2 = "import os\n" + s2
    p.write_text(s2, encoding="utf-8")
PY
      changed=$((changed+1))
    fi
  done
done

echo "Archivos modificados (aprox): $changed"
