# COGNITIVE_BOOT_PROTOCOL v1
Proyecto: Natacha / LLVC  
Estado: BASELINE OFICIAL  
Última validación: 2025-12-22  

---

## 🎯 Objetivo

Garantizar que cada nuevo contexto (chat, agente, UI, integración)
inicie desde un **estado real del sistema**, sin inferencias,
sin suposiciones y sin reescritura de código.

---

## 🧠 Principio clave

> El agente NO “recuerda por intuición”.  
> El agente LEE su estado efectivo desde el runtime.

---

## 🔁 Flujo de arranque cognitivo

### Paso 1 — Estado del sistema (runtime real)
```http
GET /ops/system/state
