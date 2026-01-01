# Natacha — Flags Registry v1.0

Este archivo define **todas** las flags válidas.
Cualquier flag fuera de esta lista está prohibida.

---

## Flags actuales

### SEMANTIC_ENGINE_ENABLED
- Tipo: boolean
- Default: 0
- Efecto:
  Activa análisis semántico pasivo
- Riesgo: bajo

---

### VECTOR_MEMORY_ENABLED
- Tipo: boolean
- Default: 0
- Efecto:
  Habilita indexación vectorial
- Riesgo: medio
- Requiere validación previa

---

### NATACHA_EXPERIMENTAL
- Tipo: boolean
- Default: 0
- Efecto:
  Permite cargar módulos no canónicos
- Uso exclusivo en staging

---

## Reglas
- Toda flag debe estar aquí
- Default siempre OFF
- Nunca romper comportamiento estable

---

Estado:
- ACTIVO
- OBLIGATORIO

