import os


def read_logs(path="logs/dashboard.log", lines=20):
    if not os.path.exists(path):
        return ["Sin logs aún."]
    with open(path) as f:
        return f.readlines()[-lines:]
