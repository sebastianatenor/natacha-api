from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    import os, hashlib
    raw = (os.getenv('API_KEY','').strip()).encode()
    sig = (hashlib.sha256(raw).hexdigest()[:8]) if raw else ''
    mode = 'dev' if os.getenv('DEV_NOAUTH')=='1' else 'locked'
    return {"status": "ok", "auth_mode": mode, "key_sig": sig}

# --- memory v2 ---
try:
    from routes.memory_v2 import router as memory_v2_router
    app.include_router(memory_v2_router)
except Exception as e:
    # No romper si falta algo en local
    print("memory_v2 not mounted:", e)
