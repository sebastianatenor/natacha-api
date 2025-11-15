# 🧠 Natacha Core — Estado del Sistema (v2025.11)

**Fecha de validación:** 2025-11-15  
**Responsable:** Sebastián Atenor  
**Proyecto:** `asistente-sebastian`  
**Región:** `us-central1`  
**Repositorio base:** `natacha-api-stable`

---

## 🌍 Infraestructura General

| Componente | Estado | Descripción |
|-------------|---------|-------------|
| **Cloud Run** | ✅ Activo | `natacha-api` y `natacha-core` desplegados en producción. |
| **Firestore** | ✅ Sincronizado | Colección principal `memory_raw` operativa y alineada con API. |
| **Storage (Backups)** | ✅ Activo | `gs://natacha-backups/` con versiones y snapshots. |
| **Docker Local** | ✅ Activo | Contenedor `natacha-brain-local` corriendo en puerto `8011`. |
| **Auth GCloud** | ✅ | Usuario `sebastianatenor@gmail.com` autenticado. |

---

## 🧠 Estado Cognitivo

| Elemento | Valor |
|-----------|-------|
| Usuario principal | `sebastian` |
| Resumen cognitivo | “Hoy tengo que hablar con Sophie por la proforma y con Jamin por las grúas que vienen desde China para LLVC…” |
| Última verificación | `2025-11-15 11:19:07` |
| Resultado | 💚 **Coherencia confirmada: Firestore y API alineados.** |

---

## 💾 Copias de Seguridad

**Ubicación general:** `gs://natacha-backups/`

| Tipo | Ejemplo | Estado |
|------|----------|--------|
| 🧠 Snapshot cognitivo | `cognitive_snapshots/cognitive_snapshot_sebastian_20251115-1059.json` | ✅ |
| ☁️ Backup Firestore | `memory_backup_20251115-1047/` | ✅ |
| 📦 Backup completo | `natacha-full-backup-20251115-1047.tar.gz` | ✅ |
| 🔁 Restauración validada | `restore_full.sh` ejecutado correctamente | ✅ |

---

## ⚙️ Automatizaciones (crontab)

| Frecuencia | Descripción | Script | Estado |
|-------------|--------------|---------|---------|
| Cada 30 min | Backup incremental de memoria | `update_mem_to_gcs.sh` | ✅ |
| 03:15 AM | Backup diario completo | `mem_backup` | ✅ |
| Cada 6 h | Verificador cognitivo | `cognition_watchdog.sh` | ✅ |
| Cada 2 h | Verificación infraestructura | `auto_infra_check.py` | ✅ |
| Diario 09:00 | Sincronización CI/CD GitHub | `refresh_failed_runs.sh` | ✅ |
| Diario 03:00 | Mantenimiento general macOS | `refresh-mac` | ✅ |

---

## ✉️ Alertas

| Tipo | Medio | Estado | Destino |
|------|--------|---------|----------|
| Desalineación cognitiva | Correo | ✅ Activo | `sebastianatenor@gmail.com` |
| Script | `send_mail_alert.sh` | ✅ | Incluido en `scripts/` |

---

## 📘 Bitácora de control

- Último backup: **2025-11-15 10:47 UTC-3**  
- Última restauración validada: **2025-11-15 10:54 UTC-3**  
- Última coherencia confirmada: **2025-11-15 11:19 UTC-3**

---

## ✅ Conclusión

> **Natacha se encuentra en estado operativo estable (v2025.11).**
>
> - Sistema cognitivo y base de datos sincronizados  
> - Copias de seguridad automáticas funcionales  
> - Restauración completa validada  
> - Monitoreo y alertas configurados  

**Estado actual:** 💚 *Estable y coherente.*

