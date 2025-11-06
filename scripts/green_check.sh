#!/usr/bin/env bash
# === Natacha: Health & Route Checker ===
# No cierra la terminal. Muestra estado de endpoints y despliegue.

set -u

SERVICE_URL="${SERVICE_URL:-https://natacha-api-422255208682.us-central1.run.app}"
TIMEOUT=8

ok(){ echo "✅ $*"; }
warn(){ echo "⚠️  $*"; }
err(){ echo "❌ $*"; }

echo "🔍 Checking service: $SERVICE_URL"
echo

# 1) Servicio base (openapi.json)
code=$(curl -s -o /dev/null -w '%{http_code}' "$SERVICE_URL/openapi.json")
if [ "$code" = "200" ]; then
  ok "OpenAPI disponible"
else
  err "OpenAPI devolvió código $code"
fi

# 2) Ping /context/ping
code=$(curl -s -o /dev/null -w '%{http_code}' "$SERVICE_URL/context/ping")
if [ "$code" = "200" ]; then
  ok "/context/ping OK"
else
  err "/context/ping -> $code"
fi

# 3) Ping alternativos
for path in /ctx/ping /ops/smart_health; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$SERVICE_URL$path")
  if [ "$code" = "200" ]; then
    ok "$path OK"
  else
    warn "$path no disponible ($code)"
  fi
done

# 4) Buscar rutas en OpenAPI
echo
echo "🔎 Rutas publicadas en OpenAPI:"
curl -s "$SERVICE_URL/openapi.json" | jq -r '.paths | keys[]' | grep -E '^/ctx/|^/ops/|^/context/' || warn "No se encontraron rutas /ctx ni /ops"

echo
echo "✅ Comprobación terminada"
