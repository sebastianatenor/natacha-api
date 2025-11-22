#!/usr/bin/env python3
"""
summary_touch_llvc.py

Refresca el updated_at del summary v1 de un user_id usando
el mismo Firestore (db) y la misma colección (COL_SUMMARY)
que usa el motor de memoria de Natacha.

Uso:
  python3 scripts/summary_touch_llvc.py --user sebastian --project LLVC
"""

import argparse
from datetime import datetime, timezone
import os
import sys

# === Asegurar que el root del proyecto esté en sys.path ===
# /Users/.../natacha-api/scripts -> /Users/.../natacha-api
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ahora sí, podemos importar como lo hace la API
from memory_engine import db, COL_SUMMARY


def parse_args():
    p = argparse.ArgumentParser(description="Refresca updated_at del summary v1 (contexto Natacha).")
    p.add_argument(
        "--user",
        "--user_id",
        dest="user_id",
        required=True,
        help="user_id a refrescar (ej: sebastian)",
    )
    p.add_argument(
        "--project",
        dest="project",
        default=None,
        help="Solo meta, para imprimir (ej: LLVC)",
    )
    return p.parse_args()


def main():
    args = parse_args()
    user_id = args.user_id
    project = args.project

    print("== SUMMARY TOUCH / REFRESH (via memory_engine.db) ==")
    print(f"user_id: {user_id} | project (lógico): {project or '-'}")
    print(f"COL_SUMMARY: {COL_SUMMARY}")

    coll = db.collection(COL_SUMMARY)

    # Intento 1: summary específico del usuario
    user_doc_ref = coll.document(user_id)
    user_snap = user_doc_ref.get()

    # Intento 2: summary global (fallback), por las dudas
    global_doc_ref = coll.document("global")
    global_snap = global_doc_ref.get()

    target_ref = None
    target_label = None
    target_snap = None

    if user_snap.exists:
        target_ref = user_doc_ref
        target_snap = user_snap
        target_label = f"user_id='{user_id}'"
    elif global_snap.exists:
        target_ref = global_doc_ref
        target_snap = global_snap
        target_label = "global"
    else:
        print(f"⚠️ No existe summary ni para user_id='{user_id}' ni para 'global' en colección '{COL_SUMMARY}'")
        return

    data = target_snap.to_dict() or {}
    prev_updated = data.get("updated_at")
    summary_text = data.get("summary") or ""

    now = datetime.now(timezone.utc).isoformat()

    print(f"\nDocumento objetivo: {target_label}")
    print("-- Estado ANTES --")
    print(f"  updated_at: {prev_updated}")
    print(f"  len(summary): {len(summary_text)} caracteres")

    # Solo refrescamos la fecha
    data["updated_at"] = now

    target_ref.set(data, merge=True)

    print("\n-- Estado DESPUÉS --")
    print(f"  updated_at: {now}")
    print(f"  len(summary): {len(summary_text)} caracteres (sin cambios)")

    print("\n✅ Summary v1 refrescado en Firestore (solo updated_at).")


if __name__ == "__main__":
    main()
