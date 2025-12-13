import json

INPUT = "memory_store.jsonl"
OUTPUT = "memory_store_cleaned.jsonl"

def clean():
    with open(INPUT, "r") as f:
        lines = f.readlines()

    cleaned = []
    for line in lines:
        try:
            obj = eval(line.strip())
            if not isinstance(obj, dict):
                continue
            if "embedding" in obj:
                del obj["embedding"]
            cleaned.append(obj)
        except Exception:
            continue

    with open(OUTPUT, "w") as f:
        for item in cleaned:
            f.write(json.dumps(item) + "\n")

    print(f"✔ Cleaned memory written to {OUTPUT}")
    print(f"✔ {len(cleaned)} valid items kept")

if __name__ == "__main__":
    clean()
