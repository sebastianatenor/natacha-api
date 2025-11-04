#!/usr/bin/env bash
set -e

echo "== Natacha intelligence report =="
# 1) preflight (tu protocolo)
if [ -f "scripts/preflight_check.sh" ]; then
  ./scripts/preflight_check.sh
else
  echo "⚠️ no existe scripts/preflight_check.sh"
fi

echo
echo "== 1) Resumen general =="
if [ -f "scripts/intelligence_summary.py" ]; then
  python3 scripts/intelligence_summary.py
else
  echo "⚠️ no existe scripts/intelligence_summary.py"
fi

echo
echo "== 2) Tareas por proyecto =="
if [ -f "scripts/intelligence_tasks.py" ]; then
  python3 scripts/intelligence_tasks.py
else
  echo "⚠️ no existe scripts/intelligence_tasks.py"
fi

echo
echo "== 3) Vencimientos =="
if [ -f "scripts/intelligence_due.py" ]; then
  python3 scripts/intelligence_due.py
else
  echo "⚠️ no existe scripts/intelligence_due.py"
fi

echo
echo "Listo ✅ (intelligence_report.sh)"
