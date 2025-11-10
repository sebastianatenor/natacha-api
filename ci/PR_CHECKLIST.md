# Natacha API – Pull Request Checklist (Canonical Guardrails)

Before merging any change into `main` or triggering a production build, verify:

## ✅ Functional Safety
☐ 1. `/health` → 200  
☐ 2. `/ops/summary?limit=1` → 200  
☐ 3. Contract unchanged (path, params, shape, keys)

## 🧩 Feature Flags
☐ 4. `SAFE_MODE`, `OPS_DISABLE_FIRESTORE`, `OPS_FORCE_BACKEND` tested  
☐ 5. Behaviour matches canonical responses (no schema drift)

## 🧪 Deployment
☐ 6. Canary deployed (0% traffic) and smoke passed  
☐ 7. Latency & 5xx rates similar to previous revision  
☐ 8. Rollback verified functional

## 📦 Documentation
☐ 9. `REGISTRY.md` updated (revision + date + notes)  
☐ 10. New routes documented or versioned under `/v1`

---

**Definition of Done:**  
If all boxes above are ✅ and Cloud Build Smoke returns 200s, the revision can be promoted from 0% → 10% → 100%.

---

*Last updated: 2025-11-10*
