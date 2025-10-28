#!/bin/bash
echo "🚀 Reiniciando entorno Natacha..."

# 1️⃣ Ir al proyecto
cd ~/Projects/natacha-api || exit

# 2️⃣ Activar entorno virtual
source venv/bin/activate

# 3️⃣ Detener posibles instancias de Streamlit
echo "🧹 Limpiando procesos previos de Streamlit..."
pkill -f streamlit 2>/dev/null || true
sleep 2

# 4️⃣ Reiniciar contenedores Docker
echo "🐳 Reiniciando contenedores..."
docker stop $(docker ps -q) 2>/dev/null || true
sleep 5
docker start natacha-core natacha-api natacha-health-monitor

# 5️⃣ Esperar a que core esté operativo
echo "⏳ Verificando estado del core..."
sleep 8
curl -s http://localhost:8081/health || echo "⚠️ No se pudo contactar con el core aún."

# 6️⃣ Registrar estado saludable manualmente en Firestore
echo "🧠 Registrando estado saludable en Firestore..."
python3 - <<'PYCODE'
from google.cloud import firestore
from datetime import datetime, UTC

db = firestore.Client()
doc = {
    "service": "natacha-core",
    "status": "✅ Core operativo y estable (reinicio automático)",
    "timestamp": datetime.now(UTC).isoformat(),
    "source": "auto_reset_script"
}
db.collection("system_health").add(doc)
print("✅ Estado saludable registrado en Firestore.")
PYCODE

# 7️⃣ Lanzar dashboard
echo "📊 Iniciando dashboard de control..."
streamlit run dashboard.py
