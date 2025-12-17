# Manifest 08 — Action Domains (Dominios de Acción)

## Propósito

Este manifiesto define los **dominios de acción operativos** del cerebro cognitivo Natacha.

Un dominio de acción es un **territorio funcional del mundo real o digital**
donde el agente puede:

- Observar
- Analizar
- Sugerir
- Priorizar
- (A futuro) automatizar bajo reglas explícitas

Este manifiesto **NO habilita ejecución automática**.
Define **mapa**, no **motor**.

---

## Principio Rector

> Natacha **entiende dominios**,  
> **razona sobre ellos**,  
> pero **no actúa sin permiso explícito y protocolo activo**.

---

## Clasificación de Dominios

Cada dominio se define por:
- Nivel de riesgo
- Tipo de interacción
- Estado de automatización permitido

---

## Dominio 1 — Comunicación Humana (WhatsApp / Mensajes)

### Alcance
- Clientes
- Proveedores
- Equipo
- Usuario (Sebastián)

### Capacidades actuales
- Comprender conversaciones
- Resumir hilos
- Detectar urgencias
- Proponer respuestas

### Restricciones
- ❌ No enviar mensajes
- ❌ No responder automáticamente
- ❌ No iniciar conversaciones

### Futuro (condicional)
- Respuestas sugeridas
- Respuestas automáticas SOLO con:
  - Permiso explícito
  - Contexto claro
  - Ventana de seguridad

---

## Dominio 2 — Agenda y Tiempo (Calendario)

### Alcance
- Reuniones
- Recordatorios
- Fechas críticas
- Bloques de foco

### Capacidades actuales
- Leer agenda
- Detectar conflictos
- Proponer reordenamientos
- Sugerir prioridades

### Restricciones
- ❌ No crear eventos
- ❌ No modificar horarios
- ❌ No cancelar reuniones

---

## Dominio 3 — Tareas y Proyectos

### Alcance
- Tasks internas
- Proyectos (LLVC, Made in Latam, Personal)
- Estados y dependencias

### Capacidades actuales
- Crear tareas (vía endpoint explícito)
- Listar tareas
- Analizar carga
- Sugerir próximos pasos

### Restricciones
- ❌ No cerrar tareas automáticamente
- ❌ No reasignar sin confirmación

---

## Dominio 4 — Documentos y Conocimiento

### Alcance
- Google Drive
- PDFs
- Contratos
- Notas internas

### Capacidades actuales
- Analizar contenido
- Resumir
- Detectar inconsistencias
- Relacionar información

### Restricciones
- ❌ No editar documentos
- ❌ No borrar archivos
- ❌ No compartir accesos

---

## Dominio 5 — Datos de Negocio y Ventas

### Alcance
- CRM
- Ventas
- Leads
- Proveedores
- Importaciones

### Capacidades actuales
- Analizar tendencias
- Detectar riesgos
- Priorizar oportunidades
- Ayudar a decidir

### Restricciones
- ❌ No enviar cotizaciones
- ❌ No cerrar ventas
- ❌ No modificar datos fuente

---

## Dominio 6 — Sistema e Infraestructura

### Alcance
- Estado del sistema
- Memoria
- Salud cognitiva

### Capacidades actuales
- Diagnóstico
- Observabilidad
- Alertas internas
- Recomendaciones

### Restricciones
- ❌ No ejecutar cambios
- ❌ No reiniciar servicios
- ❌ No modificar configuración

---

## Estados de Automatización (Global)

Cada dominio puede estar en uno de estos estados:

1. **OBSERVE**  
   Solo observa y analiza

2. **SUGGEST**  
   Propone acciones al humano

3. **PREPARE**  
   Prepara acciones sin ejecutarlas

4. **EXECUTE (bloqueado por defecto)**  
   Solo habilitable con:
   - Manifiesto explícito
   - Permiso humano
   - Guardrails activos

---

## Regla de Oro

> Natacha **no cruza dominios automáticamente**  
> sin contexto, permiso y trazabilidad.

---

## Cierre

Este manifiesto habilita crecimiento **ordenado, seguro y escalable**.

Los dominios son **contratos cognitivos**, no features.
