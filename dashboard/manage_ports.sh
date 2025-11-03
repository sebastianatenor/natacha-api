#!/bin/bash
echo "🧹 Limpiando instancias previas de Streamlit..."
pkill -f streamlit
sleep 2

echo "🚀 Iniciando Panel de Salud (8502)..."
streamlit run dashboard/system_health.py --server.port=8502 &

echo "🌐 Iniciando Dashboard General (8503)..."
streamlit run dashboard/dashboard.py --server.port=8503 &

echo "✅ Dashboards en ejecución:"
echo "   - http://localhost:8502 (Salud del sistema)"
echo "   - http://localhost:8503 (Panel central)"
