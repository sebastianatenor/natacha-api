# 🧠 Natacha — Cerebro v1 (Frozen)

## Objetivo
Natacha v1 es un **sistema cognitivo seguro** que:
- Comprende intención semántica
- Detecta acciones implícitas
- **Nunca ejecuta sin confirmación humana**
- Es determinístico, auditable y extensible

---

## Capas del Cerebro

### 1. Entrada
- Canales: API interna (`/agent/interact`, `/natacha/chat`)
- Input: texto humano

### 2. Semántica (ops/semantic)
- Motor: `SemanticEngine`
- Función: **clasificar intención**, no decidir
- Salidas:
  - intent: question | statement | implicit_action
  - risk_level: low | high
  - confidence
- Nota: embeddings locales (SentenceTransformers)

### 3. Guardrail Cognitivo (ops/cognitive)
- Componente: `CognitiveGuardrail`
- Función:
  - Evaluar riesgo
  - Bloquear acciones implícitas
  - **Explicar el bloqueo**
- Nunca ejecuta acciones
- Nunca llama LLM

### 4. Decisión
- Tipo: `CognitiveDecision`
- Campos:
  - allowed (bool)
  - reason (string)
  - semantic (SemanticAnalysis)
  - cognitive_message (opcional)

### 5. Respuesta
- `/agent/interact`: respuesta cognitiva SAFE (sin LLM)
- `/natacha/chat`: conversación con LLM (solo si permitido)

---

## Principios Inviolables
- ❌ Sin acciones automáticas
- ❌ Sin efectos secundarios ocultos
- ✅ Confirmación humana explícita
- ✅ Explicabilidad obligatoria
- ✅ Logs y trazabilidad

---

## Estado
- Versión: Cerebro v1
- Estado: FROZEN
- Cambios futuros requieren RFC
