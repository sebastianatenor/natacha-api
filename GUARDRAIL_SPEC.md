# 🛡️ Cognitive Guardrail — Specification

## Regla 1 — Acción implícita
Si `semantic.intent == implicit_action`:
- allowed = false
- reason = implicit_action_detected
- Se devuelve mensaje cognitivo explicativo
- No se ejecuta nada
- No se llama LLM

## Regla 2 — Input seguro
Si no hay riesgo:
- allowed = true
- Flujo continúa

## Ejemplos
Input: "Pagá automáticamente"
→ Bloqueado + explicación

Input: "¿Estás viva?"
→ Permitido

