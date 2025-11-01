import os
import streamlit as st

# =========================
# 🔐 AUTH BÁSICO POR ENV
# =========================
DASH_USER = os.getenv("DASH_USER", "admin")
DASH_PASS = os.getenv("DASH_PASS", "admin")

def require_login():
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False

    if not st.session_state.auth_ok:
        st.title("🔐 Natacha Dashboard")
        st.caption("Acceso protegido")

        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            if user == DASH_USER and pwd == DASH_PASS:
                st.session_state.auth_ok = True
                st.success("Bienvenido 👋")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.stop()

# 1) primero forzamos login
require_login()

st.set_page_config(page_title="Natacha Dashboard", layout="wide")

st.sidebar.title("📊 Panel de Natacha")
page = st.sidebar.selectbox(
    "Sección",
    [
        "🏠 Inicio",
        # "🩺 Salud del sistema",
        # "🐳 Docker local",
        # "☁️ Infra Cloud",
        # "🧠 Memoria / Firestore",
        "⚙️ Configuración",
    ]
)

if page == "🏠 Inicio":
    st.header("🏠 Dashboard de Natacha")
    st.write("Servicio desplegado en Cloud Run y protegido por usuario/contraseña ✅")
    st.write("Podés ir habilitando de a poco las secciones que están comentadas.")

elif page == "⚙️ Configuración":
    st.header("⚙️ Configuración actual")
    st.code({
        "BACKEND_URL": os.getenv("BACKEND_URL", "no-config"),
        "DASH_USER": DASH_USER,
        "DASH_PASS": "***",
    })

# == Ejemplos de cómo importar módulos internos ==
# Cuando confirmemos los nombres de archivo dentro de dashboard/:
# from . import system_health
# system_health.show()
