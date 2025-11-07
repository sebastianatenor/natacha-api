# 🔐 Security & API Key Playbook – Natacha API

_Last updated: '"$TS"' UTC_

---

## 🧩 Endpoints protegidos

**Protegidos por API key**
- `/memory/*`
- `/think`
- `/context`

**Exentos (públicos o diagnóstico)**
- `/`
- `/health`
- `/openapi.json`
- `/docs`
- `/redoc`
- `/memory/test`
- *(opcional dev)* `/whoami`

---

## 🧪 Cómo probar acceso

```bash
# 401 sin clave
curl -s -o /dev/null -w "%{http_code}\n" https://api.llvc-global.com/memory/search

# 200 con X-API-Key
curl -s -H "X-API-Key: $KEY_FROM_SECRET" \
  "https://api.llvc-global.com/context?topic=ai-core&limit=1" | jq .

# Alternativa con Bearer
curl -s -H "Authorization: Bearer $KEY_FROM_SECRET" \
  "https://api.llvc-global.com/context?topic=ai-core&limit=1" | jq .
