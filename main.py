
# rutas de estado (/config, /logs)
app.register_blueprint(status_bp)
app.register_blueprint(memory_export_bp)


from routes.ops_self import router as self_router
app.include_router(self_router)
