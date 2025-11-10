#!/usr/bin/env bash
set -euo pipefail

SERVICE_URL="${SERVICE_URL:?missing SERVICE_URL}"
echo "Smoke tests contra: ${SERVICE_URL}"

curl_check() {
  local path="$1"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' "${SERVICE_URL}${path}")
  echo "  ${path} -> ${code}"
  [[ "${code}" == "200" ]]
}

# Pequeño retry por si el rollout tarda
attempts=30
until curl_check "/health"; do
  ((attempts--)) || { echo "Health no levanta a tiempo"; exit 1; }
  sleep 2
done

curl_check "/ops/summary?limit=1"
curl_check "/ops/insights?limit=1"

# Opcional: deps de health si existe
code=$(curl -s -o /dev/null -w '%{http_code}' "${SERVICE_URL}/health/deps" || true)
if [[ "${code}" == "200" ]]; then
  echo "  /health/deps -> 200"
else
  echo "  /health/deps -> ${code} (ok si no existe)"
fi

echo "✅ Smoke OK"
