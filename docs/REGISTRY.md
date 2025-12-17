# REGISTRY — Natacha Cognitive System (SINGLE SOURCE OF TRUTH)

> Este archivo define el **estado vivo** del sistema Natacha.
> Todo lo que no esté acá, se considera **inactivo**.

---

## 🔧 Infraestructura Activa

### Cloud Run
- Service: natacha-api
- Region: us-central1
- Runtime: Python 3.10
- Mode: SAFE-BY-DEFAULT (no ejecución automática)

---

## 🧠 Active Cognitive Constitution

Los siguientes manifiestos están **activos**, **vigentes** y **obligatorios** para el razonamiento del sistema:

1. `00_core_cognitive_manifest`
2. `03_cognitive_guardrails`
3. `02_memory_manifest`
4. `10_execution_handshake_protocol`
5. `28_human_authority`
6. `50_fail_safe_and_degradation`
7. `05_evolution_and_scale`

Estos documentos viven en:
`docs/manifests/`

---

## 🧩 Rol del sistema

Natacha funciona como:

- Centro cognitivo persistente
- Sistema operativo ejecutivo
- Capa de razonamiento y decisión
- Orquestador de integraciones externas (NO ejecuta sin confirmación)
- Observador y evaluador de su propio estado interno

---

## 🔐 Principios no negociables

- Human-in-the-loop obligatorio
- Ninguna acción sin handshake explícito
- Autonomía gradual y reversible
- Memoria auditable
- Fallo seguro antes que acción incorrecta

---

## 📍 Estado actual

- Infraestructura: ✅ estable
- Memoria NDJSON: ✅ cargada
- Manifiestos: ✅ definidos
- Automatización: ❌ deshabilitada (por diseño)

---

> Última actualización: diciembre 2025  
> Responsable: Sebastián Atenor
