#!/usr/bin/env python3
import os, json, sys
import urllib.request

PRIMARY = "https://natacha-api-422255208682.us-central1.run.app"
SECONDARY = "https://natacha-api-422255208682.us-central1.run.app"

def fetch(url):
    with urllib.request.urlopen(url, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))

def describe(name, data):
    print(f"\n== {name} ==")
    print("tipo:", type(data).__name__)
    if isinstance(data, dict):
        print("keys:", list(data.keys()))
        if "tasks" in data:
            print(f"tareas: {len(data['tasks'])}")
    elif isinstance(data, list):
        print(f"items: {len(data)}")
        if data:
            first = data[0]
            print("primer item keys:", list(first.keys()))
    else:
        print("⚠️ forma no esperada")

def main():
    # 1) oficial
    try:
        d1 = fetch(f"{PRIMARY}/ops/summary?limit=20")
        describe("OFICIAL /ops/summary", d1)
    except Exception as e:
        print("⚠️ no pude leer del servicio OFICIAL:", e)

    # 2) secundario
    try:
        d2 = fetch(f"{SECONDARY}/ops/summary?limit=20")
        describe("SECUNDARIO /ops/summary", d2)
    except Exception as e:
        print("⚠️ no pude leer del servicio SECUNDARIO:", e)

if __name__ == "__main__":
    main()
