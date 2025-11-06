from service_main import app as _app
app = _app  # alias estable

@app.get("/__alive", include_in_schema=False)
def __alive():
    return {"ok": True, "where": "asgi->service_main", "cwd": "/app"}

@app.get("/health", include_in_schema=False)
def __health():
    return {"status": "ok", "source": "asgi-wrapper"}
