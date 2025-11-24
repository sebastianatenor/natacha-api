#!/usr/bin/env python3
"""
scripts/semantic_score.py

Objetivo:
- Recorrer un memory_store.jsonl (formato memoria v2)
- Calcular un "score" de relevancia para cada recuerdo
- Guardar un nuevo archivo con el campo "score" agregado
- NO pisa el archivo original a menos que se indique explícitamente

Uso recomendado (dry run):
  python3 scripts/semantic_score.py \
    --input data/memory_store.jsonl \
    --output data/memory_store_scored.jsonl

Más adelante podemos:
- Integrarlo a un cron
- Hacer que context_bundle use estos scores
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# Palabras clave "importantes" para tu caso LLVC / Natacha
IMPORTANT_KEYWORDS = [
    "LLVC", "LLVC Global", "maquinaria", "excavadora", "grúa",
    "XCMG", "Sophie", "Jamin", "Metalcon", "Aguas del Norte",
    "Natacha", "memory", "calendar", "Notion", "Drive"
]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Ruta al memory_store.jsonl")
    parser.add_argument("--output", required=True, help="Ruta de salida para el JSONL con score")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Si se pasa, pisa el archivo de entrada con el archivo scored"
    )
    return parser.parse_args()

def parse_dt(value):
    """Intenta parsear timestamps tipo ISO; si no puede, retorna None."""
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None

def keyword_score(text: str) -> float:
    if not text:
        return 0.0
    text_low = text.lower()
    hits = 0
    for kw in IMPORTANT_KEYWORDS:
        if kw.lower() in text_low:
            hits += 1
    # Normalizamos: 0..1 (cap a 5 hits)
    return min(hits, 5) / 5.0

def length_score(text: str) -> float:
    if not text:
        return 0.0
    words = text.split()
    # Textos demasiado cortos o demasiado largos pierden peso
    if len(words) < 5:
        return 0.1
    if len(words) > 200:
        return 0.6
    # Ideal entre 20 y 120 palabras
    ideal_min, ideal_max = 20, 120
    if ideal_min <= len(words) <= ideal_max:
        return 1.0
    # Penalización suave
    dist = min(abs(len(words) - ideal_min), abs(len(words) - ideal_max))
    return max(0.3, 1.0 - dist / 200.0)

def recency_score(created_at: str) -> float:
    if not created_at:
        return 0.5  # neutro si no sabemos
    dt = parse_dt(created_at)
    if not dt:
        return 0.5
    now = datetime.now(timezone.utc)
    days = (now - dt).days
    # 0 días -> 1.0 ; 365+ días -> 0.2
    if days <= 0:
        return 1.0
    if days >= 365:
        return 0.2
    # decaimiento lineal
    return max(0.2, 1.0 - (days / 365.0) * 0.8)

def compute_score(rec: dict) -> float:
    text = rec.get("text") or rec.get("content") or ""
    meta = rec.get("meta") or {}
    created_at = rec.get("created_at") or meta.get("created_at")

    k = keyword_score(text)
    l = length_score(text)
    r = recency_score(created_at)

    # Combinar ponderado:
    # - keywords: 0.4
    # - length: 0.2
    # - recency: 0.4
    score = 0.4 * k + 0.2 * l + 0.4 * r

    # Clamp 0..1
    score = max(0.0, min(1.0, score))
    return round(score, 4)

def main():
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"❌ Archivo de entrada no existe: {input_path}", file=sys.stderr)
        sys.exit(1)

    total = 0
    with input_path.open("r", encoding="utf-8") as fin, \
            output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                print(f"⚠️ No se pudo parsear línea: {e}", file=sys.stderr)
                continue

            score = compute_score(rec)
            # guardamos bajo una clave standard
            rec["score"] = score
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1

    print(f"✅ Proceso terminado. Registros procesados: {total}")
    print(f"➡️ Archivo de salida: {output_path}")

    if args.overwrite:
        # Reemplaza el archivo original con el scored
        backup_path = input_path.with_suffix(input_path.suffix + ".bak")
        input_path.rename(backup_path)
        output_path.rename(input_path)
        print(f"💾 Original respaldado en: {backup_path}")
        print(f"📝 Archivo scored reemplazó al original: {input_path}")

if __name__ == "__main__":
    main()
