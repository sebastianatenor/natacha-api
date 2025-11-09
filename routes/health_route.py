try:
    # FastAPI
    from fastapi import APIRouter
    router = APIRouter()
    @router.get("/health")
    def health():
        return {"status": "ok"}
except Exception:
    router = None

# Soporte Flask (si se importa desde app.py)
def register_flask(app):
    try:
        from flask import jsonify
    except Exception:
        return
    @app.route("/health", methods=["GET"])
    def health_flask():
        return jsonify(status="ok")
