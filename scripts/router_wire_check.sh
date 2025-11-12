#!/usr/bin/env bash
set -euo pipefail

BASE="${NATACHA_BASE_URL:-${REPO_BASE_URL:-${BASE:-}}}"
if [[ -z "${BASE:-}" ]]; then
  echo "🔴 BASE no definido (NATACHA_BASE_URL / REPO_BASE_URL / BASE)"; exit 1
fi

say() { echo -e "$*"; }

# hit <method> <path> [data-json]
hit() {
  local m="$1" p="$2" d="${3:-}"
  local url="${BASE%/}${p}"
  say "→ ${m} ${p}"
  local resp code
  resp="$(mktemp)"
  if [[ -n "$d" ]]; then
    code="$(curl -sS -w '%{http_code}' -o "$resp" -H 'Content-Type: application/json' -X "$m" --data "$d" "$url" || true)"
  else
    code="$(curl -sS -w '%{http_code}' -o "$resp" -X "$m" "$url" || true)"
  fi

  if [[ "$code" =~ ^2[0-9][0-9]$ ]]; then
    say "🟢 ${m} ${p} (${code})"
    return 0
  else
    say "🔴 ${m} ${p} (${code})"
    say "── body ──"; cat "$resp" || true; say "──────────"
    return 1
  fi
}

say "🔎 Wirecheck contra BASE=$BASE"

# 1) health
hit GET /health

# 2) memory/add (payload válido + fallback a /v1/memory/add)
PAYLOAD='{"summary":"ci-wirecheck","detail":"wirecheck probe","project":"Natacha","channel":"ci"}'
if ! hit POST /memory/add "$PAYLOAD"; then
  say "⚠️ fallback a /v1/memory/add"
  hit POST /v1/memory/add "$PAYLOAD" || exit 1
fi

# 3) memory/search (fallback a v1)
if ! hit GET "/memory/search?limit=1&query=wirecheck"; then
  say "⚠️ fallback a /v1/memory/search"
  hit GET "/v1/memory/search?limit=1&query=wirecheck" || exit 1
fi

# 4) tasks search (v1, fallback a /tasks/list)
if ! hit GET "/v1/tasks/search?limit=1"; then
  say "⚠️ fallback a /tasks/list"
  hit GET "/tasks/list?limit=1" || exit 1
fi

say "✅ Wirecheck PASS"
