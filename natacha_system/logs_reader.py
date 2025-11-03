import os


def read_recent_logs(path="logs", lines=20):
    if not os.path.exists(path):
        return ["[No hay logs disponibles]"]
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".log")]
    if not files:
        return ["[No se encontraron archivos de log]"]
    latest = max(files, key=os.path.getmtime)
    with open(latest, "r", encoding="utf-8", errors="ignore") as f:
        content = f.readlines()
    return content[-lines:]
