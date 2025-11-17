# Changelog

## 🧩 v19.0 – Adaptive Affective Training
**Fecha:** 2025-11-16  
**Autor:** @sebastianatenor  
**Tipo:** Feature Release  
**Codename:** *Adaptive Affective Training*

### 🧠 Descripción
Versión 19.0 introduce la primera capa del **ciclo adaptativo afectivo**, una nueva arquitectura que permite a Natacha-Core simular procesos de **autoajuste emocional** basados en contexto y estado interno.  
Esta release marca el inicio del *Affective Projection Engine* dentro del subsistema `/ops`.

---

### ✨ Nuevas funcionalidades
#### 🔹 Módulo de entrenamiento afectivo (`ops/affective_train.py`)
- Endpoint: `POST /ops/affective-train/run`
- Genera una proyección afectiva simulada con valores de:
  - Estado de ánimo (`predicted_mood`)
  - Energía (`predicted_energy`)
  - Nivel de confianza (`confidence`)
- Permite evaluar el pipeline de *proyección cognitivo-afectiva* antes de conectar con el `adaptive_trainer`.

#### 🔹 Nueva métrica base (`natacha_core/metrics/affective_metrics.py`)
- Introduce estructura de métricas para registrar parámetros de predicción afectiva.  
- Servirá como base para las correlaciones longitudinales (v19.1+).

#### 🔹 Integración modular automática
- Registro mediante `safe_include("ops.affective_train")` dentro de `service_main.py`.  
- Compatible con versiones previas del Core Bridge y del esquema OpenAPI.

---

### 🧪 Validaciones
- ✅ Build Docker (`natacha-brain-local`) exitoso.  
- ✅ Import manual validado dentro del contenedor (`import ops.affective_train`).  
- ✅ Safe include activo y visible en `app.routes`.  
- ✅ Tag `v19.0` generado y publicado.

---

### 🧭 Estructura introducida

## stable-20251108-012435 – 2025-11-08 (UTC)

**Diff:** https://github.com/sebastianatenor/natacha-api/compare/stable-20251108-011344...stable-20251108-012435

### Docs
- docs: add code of conduct (c3f813c) — Sebastián Atenor
- docs: show CI badges (Sanity + Tag Sanity) (4b25f34) — Sebastián Atenor

### Commits
- ci: remove auto-tag on main push (f58f97d) — GitHub Actions
- ci: changelog & release on stable-* tags (362f593) — GitHub Actions
- ci: auto-tag stable on main push (6bf9394) — Sebastián Atenor
- docs: add code of conduct (c3f813c) — Sebastián Atenor
- docs: show CI badges (Sanity + Tag Sanity) (4b25f34) — Sebastián Atenor


- 🧠 v19.2 – Cloud Memory Sync Edition (auto GCS memory load)
- 🧠 v19.3 – Cognitive Evolution + Self Diagnostics + Firestore Bridge (Stable Release)
