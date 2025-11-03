import os
import socket
import subprocess
import sys


def find_free_port(default=8503):
    port = default
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
            port += 1


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

port = find_free_port()
print(f"🚀 Iniciando Streamlit en el puerto {port}...")

subprocess.run(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard/dashboard.py",
        "--server.port",
        str(port),
    ]
)
