# Natacha — Arquitectura Canónica v1.0

## Principio rector
Natacha funciona como **una única unidad cognitiva**, aunque esté desplegada en servicios separados.

> Unidad lógica > separación física

---

## Componentes principales

### 1. Gateway — natacha-api
Responsabilidad:
- Punto único de entrada público
- Exposición de OpenAPI
- Healthcheck
- Proxy cognitivo

Endpoints clave:
- /health
- /agent/interact
- /ops/system/*

NO contiene:
- lógica cognitiva profunda
- decisiones
- ejecución de acciones

---

### 2. Núcleo Cognitivo — ops/*
Responsabilidad:
- Evaluación cognitiva
- Guardrails
- Percepción del sistema
- Baseline
- Respuesta determinística

Componentes:
- ops/agent
- ops/cognitive
- ops/core/respond.py

---

### 3. Memoria
Tipo:
- NDJSON canónica

Características:
- Persistente
- Independiente del código
- Sobrevive deploys
- Restaurable por snapshot

Ruta:
- Local: ./memory_store.jsonl
- Cloud Run: /tmp/memory_store.jsonl

---

### 4. Semántica
Estado actual:
- Heurística
- Pasiva
- No decisoria

Activación:
- Solo vía flag

---

## Flujo cognitivo

Usuario
  ↓
/agent/interact
  ↓
Percepción → Guardrail → Respond
  ↓
Respuesta determinística

---

## Regla de oro
Si /agent/interact responde correctamente,
**Natacha está operativa**.

---

Estado:
- CANÓNICO
- NO EXPERIMENTAL
- BASE DE TODO DEPLOY

