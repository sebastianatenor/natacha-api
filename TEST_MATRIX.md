# Natacha — Test Matrix v1.0

Define qué se testea **antes** de un deploy
y qué NO.

---

## Tests obligatorios (BLOCKERS)

### Runtime local
- /health → 200
- /agent/interact → responde estado
- /openapi.json → carga sin crash

---

### Código
- Imports críticos OK:
  - ops.agent.interact
  - ops.core.respond
  - ops.cognitive.guardrail

- python -m py_compile service_main.py

---

### Memoria
- Archivo accesible
- No se borra
- No se versiona en git

---

## Tests recomendados (NO bloqueantes)
- Semantic engine OFF
- Flags default OFF
- OpenAPI sin warnings críticos

---

## NO se testea antes de deploy
- Calidad de respuestas
- Performance avanzada
- Features futuras
- Refactors estéticos

---

## Regla final
Si los tests obligatorios pasan,
**SE DEPLOYA UNA SOLA VEZ**.

---

Estado:
- CANÓNICO
- BASE DE DEPLOY

