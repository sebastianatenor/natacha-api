import streamlit.components.v1 as components
from pyvis.network import Network

st.divider()
st.header("6️⃣ Mapa de Infraestructura Global 🌍")

# Crear red
net = Network(
    height="600px", width="100%", bgcolor="#0E1117", font_color="white", directed=True
)
net.toggle_physics(True)

# === NODOS PRINCIPALES ===
net.add_node(
    "Infraestructura",
    shape="ellipse",
    color="#E67E22",
    size=40,
    title="Centro de control general",
)

# Docker
net.add_node(
    "Docker", shape="box", color="#3498DB", title="Infraestructura local (contenedores)"
)
net.add_edge("Infraestructura", "Docker")

# Cloud
net.add_node(
    "Cloud Run",
    shape="box",
    color="#2ECC71",
    title="Servicios desplegados en Google Cloud Run",
)
net.add_edge("Infraestructura", "Cloud Run")

# Firestore
net.add_node(
    "Firestore", shape="box", color="#F39C12", title="Base de datos en la nube"
)
net.add_edge("Infraestructura", "Firestore")

# FHIR
net.add_node(
    "FHIR", shape="box", color="#9B59B6", title="Almacenamiento de datos clínicos"
)
net.add_edge("Infraestructura", "FHIR")

# Integraciones
net.add_node(
    "Integraciones", shape="box", color="#1ABC9C", title="Servicios externos conectados"
)
net.add_edge("Infraestructura", "Integraciones")

# === DOCKER CONTAINERS ===
try:
    for c in containers:
        color = "#58D68D" if c.status == "running" else "#E74C3C"
        net.add_node(
            c.name, shape="dot", color=color, title=f"Contenedor {c.name} ({c.status})"
        )
        net.add_edge("Docker", c.name)
except Exception:
    pass

# === CLOUD RUN ===
try:
    for s in services:
        name = s["metadata"]["name"]
        url = s["status"].get("url", "")
        net.add_node(
            name, shape="dot", color="#27AE60", title=f"Servicio Cloud Run\n{url}"
        )
        net.add_edge("Cloud Run", name)
        # Conexiones lógicas básicas
        if "core" in name:
            net.add_edge(name, "Firestore")
        if "api" in name:
            net.add_edge(name, "natacha-core")
except Exception:
    pass

# === INTEGRACIONES ===
integrations_nodes = [
    ("natacha-whatsapp", "WhatsApp", "#1EBEA5"),
    ("natachaspeak", "Speech", "#9B59B6"),
    ("natacha-plugin-registry", "Plugin Registry", "#E74C3C"),
]
for key, label, color in integrations_nodes:
    net.add_node(label, shape="diamond", color=color, title=f"Integración {label}")
    net.add_edge("Integraciones", label)
    net.add_edge("Cloud Run", label)

# Renderizar red en HTML temporal
tmp_file = "/tmp/natacha_infra_map.html"
net.save_graph(tmp_file)

# Insertar dentro de Streamlit
components.html(open(tmp_file, "r").read(), height=650)
