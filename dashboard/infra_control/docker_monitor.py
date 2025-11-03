from datetime import datetime

import docker
import pandas as pd
import streamlit as st


def show():
    st.title("🐳 Docker — Estado de Contenedores e Imágenes")
    st.caption("Monitoreo local de la infraestructura Docker activa")

    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        images = client.images.list()
        networks = client.networks.list()

        # --- Contenedores
        st.subheader("📦 Contenedores")
        if containers:
            data = []
            for c in containers:
                stats = c.attrs
                ports = stats["NetworkSettings"]["Ports"]
                data.append(
                    {
                        "Nombre": c.name,
                        "ID": c.short_id,
                        "Imagen": c.image.tags[0] if c.image.tags else "Sin etiqueta",
                        "Estado": c.status,
                        "Puertos": ", ".join(
                            [
                                f"{k}->{v[0]['HostPort']}" if v else k
                                for k, v in (ports or {}).items()
                            ]
                        ),
                    }
                )
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay contenedores activos o detenidos.")

        # --- Imágenes
        st.subheader("🖼️ Imágenes disponibles")
        if images:
            df_img = pd.DataFrame(
                [
                    {
                        "ID": img.short_id,
                        "Etiqueta": img.tags[0] if img.tags else "Sin etiqueta",
                        "Tamaño (MB)": round(img.attrs["Size"] / (1024 * 1024), 2),
                    }
                    for img in images
                ]
            )
            st.dataframe(df_img, use_container_width=True)
        else:
            st.info("No hay imágenes locales.")

        # --- Redes
        st.subheader("🌐 Redes configuradas")
        if networks:
            df_net = pd.DataFrame(
                [
                    {
                        "Nombre": net.name,
                        "Driver": net.attrs["Driver"],
                        "Scope": net.attrs["Scope"],
                    }
                    for net in networks
                ]
            )
            st.dataframe(df_net, use_container_width=True)
        else:
            st.info("No hay redes Docker configuradas.")

        # --- Estadísticas generales
        st.subheader("📊 Resumen general")
        col1, col2, col3 = st.columns(3)
        col1.metric("Contenedores", len(containers))
        col2.metric("Imágenes", len(images))
        col3.metric("Redes", len(networks))

    except docker.errors.DockerException as e:
        st.error("⚠️ No se pudo conectar al demonio Docker.")
        st.code(str(e))
    except Exception as e:
        st.error("🚨 Error inesperado al leer Docker:")
        st.code(str(e))

    st.caption(
        f"Última actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
