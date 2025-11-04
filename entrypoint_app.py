from fastapi import FastAPI
import os, hashlib, traceback

app = FastAPI(title="Natacha API (entrypoint)")

@app.get("/__alive")
def __alive():
    return {"ok": True, "where": "entrypoint_app", "cwd": os.getcwd()}

@app.get("/__sha")
def __sha():
    try:
        with open(__file__, "rb") as fh:
            return {"file": __file__, "sha256": hashlib.sha256(fh.read()).hexdigest()}
    except Exception as e:
        return {"error": str(e)}

IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}
