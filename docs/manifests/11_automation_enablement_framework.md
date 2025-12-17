# Manifest 11 — Automation Enablement Framework
(Marco de Habilitación de Automatización)

## Propósito

Este manifiesto define **cuándo**, **dónde** y **bajo qué condiciones**
el cerebro cognitivo Natacha puede comenzar a **automatizar acciones reales**.

La automatización:
- No es un salto
- No es global
- No es irreversible

Es **incremental, evaluada y revocable**.

---

## Principio Rector

> Primero entender.  
> Luego sugerir.  
> Luego preparar.  
> Solo después automatizar.

---

## Niveles de Automatización

La automatización se habilita por **niveles**, no por features.

---

### Nivel 0 — OBSERVE (Default)

Estado inicial de todos los dominios.

Capacidades:
- Analizar
- Observar
- Detectar patrones
- Alertar

Restricciones:
- ❌ No sugerir acciones ejecutables
- ❌ No preparar acciones
- ❌ No actuar

📌 Este nivel **nunca se desactiva**.

---

### Nivel 1 — SUGGEST

Automatización cognitiva, no operativa.

Capacidades:
- Sugerir acciones
- Priorizar opciones
- Explicar impactos

Restricciones:
- ❌ No preparar ejecución
- ❌ No ejecutar

Requisitos:
- Manifest 07 activo
- Guardrails cognitivos activos

---

### Nivel 2 — PREPARE

Automatización preparatoria.

Capacidades:
- Redactar borradores
- Armar propuestas
- Simular acciones
- Generar checklists

Restricciones:
- ❌ No ejecutar
- ❌ No enviar
- ❌ No modificar sistemas externos

Requisitos:
- Confirmación humana por acción
- Manifest 10 (handshake) activo

---

### Nivel 3 — ASSISTED EXECUTION

Automatización asistida.

Capacidades:
- Ejecutar acciones simples
- En un solo dominio
- Bajo supervisión humana

Ejemplos:
- Enviar un mensaje aprobado
- Crear una tarea confirmada
- Agendar un evento validado

Restricciones:
- ❌ No acciones encadenadas
- ❌ No decisiones implícitas
- ❌ No múltiples dominios

Requisitos:
- Manifest 08 (dominios) habilitado
- Manifest 09 (permisos) explícito
- Manifest 10 (handshake) completo

---

### Nivel 4 — CONDITIONAL AUTOMATION

Automatización condicional.

Capacidades:
- Ejecutar acciones repetitivas
- Bajo reglas estrictas
- En contextos bien definidos

Ejemplos:
- Respuestas automáticas tipo “recibido”
- Recordatorios programados
- Actualizaciones de estado internas

Restricciones:
- ❌ No excepciones no previstas
- ❌ No aprendizaje autónomo
- ❌ No decisiones estratégicas

Requisitos:
- Historial sin errores
- Validación humana previa
- Ventana de rollback

---

### Nivel 5 — AUTONOMOUS MICRO-ACTIONS (Bloqueado por defecto)

⚠️ Este nivel **NO está habilitado** por este manifiesto.

Requiere:
- Manifiesto específico
- Auditoría
- Métricas
- Kill-switch activo

---

## Reglas de Habilitación

La automatización se habilita **por dominio**, no globalmente.

Cada dominio debe declarar:
- Nivel máximo permitido
- Tipos de acciones
- Contextos válidos
- Condiciones de bloqueo

---

## Reglas de Reversibilidad

Toda automatización debe ser:
- Desactivable
- Auditable
- Reversible

Si algo falla:
→ El sistema vuelve automáticamente a **Nivel 1 (SUGGEST)**.

---

## Métricas de Preparación

Un dominio puede subir de nivel solo si:

- ✔️ Baja tasa de error
- ✔️ Confirmaciones claras
- ✔️ Contexto estable
- ✔️ Usuario consistente

---

## Relación con otros manifiestos

- Manifest 07 → define readiness
- Manifest 08 → define dominios
- Manifest 09 → define permisos
- Manifest 10 → define ejecución
- Manifest 11 → define automatización

---

## Regla de Oro Final

> Automatizar sin comprensión es delegar el caos.

---

## Cierre

Este manifiesto convierte a Natacha en:
- Un sistema confiable
- Un socio escalable
- Un cerebro que crece con vos

No acelera por ansiedad.  
Acelera por madurez.
