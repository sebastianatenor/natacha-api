import logging

def setup_logging(app):
    """
    Configura logs estándar para todos los servicios.
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info(f"✅ Logging inicializado para {app.config['SERVICE_NAME']}")

