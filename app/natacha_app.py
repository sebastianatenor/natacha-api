
# === DEBUG GLOBAL DE EXCEPCIONES ===
import logging, traceback
from fastapi import Request
from fastapi.responses import PlainTextResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("natacha")

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[UNCAUGHT] {request.method} {request.url} -> {e}\n{tb}")
        return PlainTextResponse("Internal Server Error", status_code=500)

@app.exception_handler(Exception)
async def all_exceptions_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    logger.error(f"[HANDLER] {request.method} {request.url} -> {exc}\n{tb}")
    return PlainTextResponse("Internal Server Error", status_code=500)
