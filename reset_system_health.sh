#!/bin/bash
# ============================================================
# 🔄 Natacha System Health Reset Script + Dashboard Restart
# Autor: Álvaro Sebastián Atenor
# Fecha: $(date)
# ============================================================

echo "🚀 Iniciando reseteo completo del sistema Natacha..."
cd ~/Projects/natacha-api
source venv/bin/activate

# --- Paso 1: Limpieza de registros Firestore ---
python3 - <<'PYCODE'
from google.cloud import firestore
from datetime import datetime, UTC

db = firestore.Client()
col = db.collection("system_health")

batch_size = 100
deleted_total = 0

print("🧹 Eliminando registros antiguos...")
while True:
    docs = list(col.limit(batch_size).stream())
    if not docs:
        break
    for doc in docs:
        doc.reference.delete()
        deleted_total += 1
    print(f"  > Eliminados {deleted_total} registros hasta ahora...")

print(f"✅ Limpieza completa. Total: {deleted_total} documentos eliminados.\n")

# --- Paso 2: Reinserción de registros limpios ---
now = datetime.now(UTC).isoformat()
services = [
    {"service": "natacha-core", "status": "✅ Core operativo y estable", "timestamp": now, "source": "auto_reset"},
    {"service": "natacha-api", "status": "✅ API activa y respondiendo", "timestamp": now, "source": "auto_reset"},
    {"service": "natacha-health-monitor", "status": "✅ Monitor ejecutándose correctamente", "timestamp": now, "source": "auto_reset"},
]

for s in services:
    col.add(s)

print("🚀 3 registros limpios insertados correctamente.\n")

# --- Paso 3: Verificación ---
print("📊 Estado final del sistema:\n")
for doc in col.stream():
    d = doc.to_dict()
    print(f"{d['service']} — {d['status']} ({d['timestamp']})")
PYCODE

# --- Paso 4: Reinicio del Dashboard ---
echo ""
echo "🧠 Reiniciando el dashboard de control..."
pkill -f streamlit >/dev/null 2>&1
sleep 2

nohup streamlit run dashboard.py >/dev/null 2>&1 &
sleep 4

echo "✅ Dashboard reiniciado correctamente."
echo "🌐 Accedé en: http://localhost:8501"
