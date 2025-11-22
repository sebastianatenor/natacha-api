#!/usr/bin/env bash
set -e

BASE="https://natacha-api-422255208682.us-central1.run.app"

echo "== PEOPLE: SAVE Sophie =="
curl -s "$BASE/people/save" \
  -X POST -H "Content-Type: application/json" \
  -d '{
    "id":"sophie_xcmg",
    "name":"Sophie",
    "role":"Sales - XCMG",
    "location":"Xuzhou",
    "notes":"Demoras en proformas, contacto principal para LLVC",
    "tags":["china","xcmg","proformas","llvc"]
  }' | jq .

echo
echo "== PEOPLE: GET Sophie =="
curl -s "$BASE/people/get?user_id=sophie_xcmg" | jq .

echo
echo "== PEOPLE: SEARCH (limit=10) =="
curl -s "$BASE/people/search?limit=10" | jq .

echo
echo "== PROJECTS: SAVE LLVC =="
curl -s "$BASE/projects/save" \
  -X POST -H "Content-Type: application/json" \
  -d '{
    "id": "LLVC",
    "name": "LLVC Global",
    "status": "activo",
    "focus": ["importaciones","maquinaria","sourcing"],
    "notes": "Proyecto principal con China",
    "risks": ["demoras proformas","costos logísticos"],
    "next_steps": ["cerrar PI Sophie","hablar con Jamin","actualizar deck clientes"]
  }' | jq .

echo
echo "== PROJECTS: GET LLVC =="
curl -s "$BASE/projects/get?project_id=LLVC" | jq .

echo
echo "== PROJECTS: SEARCH (limit=10) =="
curl -s "$BASE/projects/search?limit=10" | jq .
