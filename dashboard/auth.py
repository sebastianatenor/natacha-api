import os

import streamlit as st


def check_login():
    user_env = os.getenv("DASH_USER")
    pass_env = os.getenv("DASH_PASS")

    # si no hay credenciales en el entorno, no bloqueamos
    if not user_env or not pass_env:
        return True

    # usamos el state de streamlit
    if "auth_ok" in st.session_state and st.session_state["auth_ok"]:
        return True

    st.title("🔐 Natacha Dashboard")
    st.caption("Acceso restringido · LLVC")

    user = st.text_input("Usuario", value="", key="login_user")
    pw = st.text_input("Contraseña", value="", type="password", key="login_pass")

    ok = st.button("Ingresar")

    if ok:
        if user == user_env and pw == pass_env:
            st.session_state["auth_ok"] = True
            st.success("✅ Acceso concedido. Cargá de nuevo el dashboard.")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()
