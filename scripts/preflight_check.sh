. "$(dirname "$0")/../tools/canon_resolver.sh" || source tools/canon_resolver.sh
resolve_canon # exporta CANONICAL
#!/usr/bin/env bash
set -e

EXPECTED_PROJECT="asistente-sebastian"
EXPECTED_REGION="us-central1"
EXPECTED_ACCOUNT="sebastianatenor@gmail.com"

CUR_PROJECT=$(gcloud config get-value project 2>/dev/null | tr -d '\r')
CUR_REGION=$(gcloud config get-value run/region 2>/dev/null | tr -d '\r')
CUR_ACCOUNT=$(gcloud config get-value account 2>/dev/null | tr -d '\r')

echo "== Natacha preflight =="
echo "Proyecto actual : $CUR_PROJECT"
echo "Región actual   : $CUR_REGION"
echo "Cuenta actual   : $CUR_ACCOUNT"
echo

ERR=0
if [ "$CUR_PROJECT" != "$EXPECTED_PROJECT" ]; then
  echo "❌ Proyecto NO es $EXPECTED_PROJECT"
  ERR=1
fi

if [ "$CUR_REGION" != "$EXPECTED_REGION" ]; then
  echo "❌ Región NO es $EXPECTED_REGION"
  ERR=1
fi

if [ "$CUR_ACCOUNT" != "$EXPECTED_ACCOUNT" ]; then
  echo "⚠️ Cuenta no es la esperada ($EXPECTED_ACCOUNT) → revisar"
fi

if [ $ERR -ne 0 ]; then
  echo
  echo "⛔ Abortando porque el entorno no es el esperado."
  exit 1
fi

echo "✅ Entorno OK, podés seguir."

# --- inteligencia de vencimientos (auto) ---
if [ -f "scripts/intelligence_due.py" ]; then
  echo "\n== Vencimientos detectados =="
  python3 scripts/intelligence_due.py
else
  echo "⚠️ scripts/intelligence_due.py no existe todavía"
fi
