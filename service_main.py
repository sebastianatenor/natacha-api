from patches.limiter_safe_patch import safe_limit
from patches.limiter_safe_patch import safe_limit





# --- safe import for get_db/get_client ---
try:
    from routes.db_util import get_db, get_client
except Exception:  # define fallbacks so the app can boot
    from contextlib import contextmanager
    def get_client():
        return None
    @contextmanager
    def get_db():
        yield None
# --- end safe import block ---

# === optional SlowAPI integration (safe) ===
Limiter = None
get_remote_address = None
SlowAPIMiddleware = None
RateLimitExceeded = Exception
try:
    from slowapi import Limiter as _Limiter
    from slowapi.util import get_remote_address as _get_remote_address
    from slowapi.middleware import SlowAPIMiddleware as _SlowAPIMiddleware
    from slowapi.errors import RateLimitExceeded as _RateLimitExceeded
    Limiter = _Limiter
    get_remote_address = _get_remote_address
    SlowAPIMiddleware = _SlowAPIMiddleware
    RateLimitExceeded = _RateLimitExceeded
except Exception:
    pass
# === end optional SlowAPI integration ===

# --- safe import for get_db/get_client ---
try:
    pass  # auto-added to fix empty try
except Exception:
    from contextlib import contextmanager
    def get_client():
        return None
    @contextmanager
    def get_db():
        yield None

# -- safe import for db_util (fallback if missing) --
try:
    pass  # auto-added to fix empty try
except Exception:  # define fallbacks so the app can boot
    from contextlib import contextmanager
    def get_client():
        return None
    @contextmanager
    def get_db():
        yield None

Limiter = None
get_remote_address = None
SlowAPIMiddleware = None
RateLimitExceeded = Exception
try:
    # Try importing slowapi if available
    Limiter = _Limiter
    get_remote_address = _get_remote_address
    SlowAPIMiddleware = _SlowAPIMiddleware
    RateLimitExceeded = _RateLimitExceeded
except Exception:
    # slowapi no instalado: seguimos sin rate limiting
    pass

import uuid
from fastapi import FastAPI, Request, HTTPException, Query

Limiter = None
get_remote_address = None
SlowAPIMiddleware = None
RateLimitExceeded = Exception
try:
    # Try importing slowapi if available
    Limiter = _Limiter
    get_remote_address = _get_remote_address
    SlowAPIMiddleware = _SlowAPIMiddleware
    RateLimitExceeded = _RateLimitExceeded
except Exception:
    # slowapi no instalado: seguimos sin rate limiting
    pass


try:
    pass
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception


try:
    pass
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception


try:
    pass
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception

try:
    pass
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception

from typing import Optional, List, Dict, Any
from google.cloud import firestore
from fastapi import FastAPI, Query, Request, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from routes.health_routes import router as health_router
from routes.cog_routes import router as cog_router
from routes.actions_routes import router as actions_router
from routes.tasks_routes import router as tasks_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib, traceback
from routes.auto_routes import router as auto_router

# Configurar limitador global (por IP)
async def ratelimit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests – please wait a moment."})

# Configurar limitador global (por IP)

# Configurar limitador global (por IP)

from fastapi.responses import JSONResponse

# Configurar limitador global (por IP)

async def ratelimit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests – please wait a moment."})

app = FastAPI()

@app.get("/__debug_routes")
def __debug_routes():
    from fastapi.routing import APIRoute
    items = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            items.append({
                "path": r.path,
                "methods": sorted(list(r.methods)),
                "in_schema": getattr(r, "include_in_schema", None)
            })
    return {"count": len(items), "routes": items}

    limiter = (Limiter or (lambda *a, **k: None))(key_func=get_remote_address)
    app.state.limiter = limiter
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
if SlowAPIMiddleware:
    app.add_middleware(SlowAPIMiddleware)
app.include_router(health_router)
app.include_router(cog_router)
app.include_router(actions_router)

app.include_router(tasks_router)

app.add_middleware(CORSMiddleware, allow_origins=["https://dashboard.llvc-global.com","https://natacha-dashboard-422255208682.us-central1.run.app"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auto_router)

@app.get("/__alive")
def __alive():
    return {"ok": True, "where": "service_main", "cwd": os.getcwd()}

@app.get("/__sha")
def __sha():
    try:
        with open(__file__, "rb") as fh:
            return {"file": __file__, "sha256": hashlib.sha256(fh.read()).hexdigest()}
    except Exception as e:
        return {"error": str(e)}

# Routers opcionales (no rompe si faltan)
IMPORT_ERR = None
try:
    from routes import ops_routes
    app.include_router(ops_routes.router)
except Exception as e:
    IMPORT_ERR = "".join(traceback.format_exception_only(type(e), e)).strip()

@app.get("/__ops_import_status")
def __ops_import_status():
    return {"import_ok": IMPORT_ERR is None, "error": IMPORT_ERR}

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     schema = get_openapi(title=app.title, version=app.version, routes=app.routes, description="Natacha API")
#     public = os.getenv("OPENAPI_PUBLIC_URL","").rstrip("/")
#     if public:
#         schema["servers"] = [{"url": public}]
#     schema["openapi"] = "3.1.0"
#     app.openapi_schema = schema
#     return app.openapi_schema
# 
# app.openapi_schema = None
# app.openapi = custom_openapi

# /openapi.v1.json compat
try:
    from routes.openapi_compat import router as openapi_router
    app.include_router(openapi_router)
except Exception:
    pass
# --- Health at root (idempotente) ---
try:
    app
except NameError:
    from fastapi import FastAPI
# #     app = FastAPI()  # DUPLICATE REMOVED  # DUPLICATE REMOVED

# --- FINAL fallback health (direct on app) ---
try:
    app
except NameError:
    from fastapi import FastAPI
# #     app = FastAPI()  # DUPLICATE REMOVED  # DUPLICATE REMOVED

def health_final():
    return {"status": "ok (fallback)"}

# --- Canonical /health (must be after final app assignment) ---
try:
    app
except NameError:
    from fastapi import FastAPI
# #     app = FastAPI()  # DUPLICATE REMOVED  # DUPLICATE REMOVED

def health():
    return {"status": "ok"}

# === Debug: saber desde dónde corre Uvicorn y qué rutas hay ===
from fastapi import APIRouter
_debug_router = APIRouter()

@_debug_router.get("/__whoami", include_in_schema=False)
def __whoami():
    import inspect
    return {
        "module": __name__,
        "file": __file__,
        "app_type": str(type(app)),
        "routes_count": len(app.router.routes),
    }

    # If something odd happens during import, fail visibly in logs
    print("WARN: could not register /health on service_main:", e)
    print("WARN inject diag failed:", _e)

@app.get("/config")
async def _config():
    return {
        "service": os.getenv("SERVICE_NAME","natacha-api"),
        "project": os.getenv("GOOGLE_CLOUD_PROJECT","asistente-sebastian"),
        "revision": os.getenv("K_REVISION","local"),
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/logs")
async def _logs(limit: int = 10):
    now = datetime.now(timezone.utc).isoformat()
    logs = [{"timestamp": now, "severity": "INFO", "message": f"stub log {i+1}"} for i in range(max(1, min(limit, 100)))]
    return JSONResponse(logs)
# === Memory Test Stub (idempotente) ===
try:
    app
except NameError:
    from fastapi import FastAPI
#     app = FastAPI()  # DUPLICATE REMOVED

if not any(getattr(r, "path", "") == "/memory/test" for r in getattr(app, "routes", [])):
    @app.get("/memory/test")
    def memory_test():
        return {
            "status": "memory-endpoints-available",
            "backend": "stub",
            "note": "replace with Firestore-backed endpoints later"
        }


# === Firestore-backed memory endpoints ===
def _fs_client():
    return firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian"))

def _to_list(v):
    if v is None: return []
    if isinstance(v, list): return v
    if isinstance(v, str): return [t.strip() for t in v.split(",") if t.strip()]
    return [str(v)]

@app.post("/memory/put")
async def memory_put(request: Request):
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        data = await request.json()
    else:
        data = dict((await request.form()).items())

    text  = (data.get("text") or "").strip()
    topic = (data.get("topic") or "general").strip()
    scope = (data.get("scope") or "global").strip()
    tags  = _to_list(data.get("tags"))

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    doc = {
        "text": text,
        "topic": topic,
        "scope": scope,
        "tags": tags,
        "ts": datetime.utcnow().isoformat() + "Z",
    }
    db = _fs_client()
    ref = db.collection("natacha_memory").add(doc)[1]
    return {"ok": True, "id": ref.id, "stored": doc}

# --- Limiter fallback (DEBE estar antes de cualquier @limiter.limit) ---
try:
    limiter
except NameError:
    limiter = (Limiter or (lambda *a, **k: None))(key_func=get_remote_address)

@safe_limit(limiter)("30/minute")
@app.get("/memory/search")
async def memory_search(request: Request, q: str = Query("", alias="q"),
                        topic: Optional[str] = None,
                        limit: int = 20):
    limit = max(1, min(int(limit or 20), 100))
    db = _fs_client()
    qry = db.collection("natacha_memory").order_by("ts", direction=firestore.Query.DESCENDING).limit(200)
    docs = [d.to_dict() | {"_id": d.id} for d in qry.stream()]
    if topic:
        docs = [d for d in docs if (d.get("topic") or "").lower() == topic.lower()]
    if q:
        ql = q.lower()
        docs = [d for d in docs if ql in (d.get("text","").lower() + " " + " ".join(d.get("tags",[])).lower())]
    return {"ok": True, "count": len(docs[:limit]), "items": docs[:limit]}

def _fs():
    # Usa credenciales por defecto de Cloud Run
    return firestore.Client()

@app.post("/think")
async def think(req: Request):
    """Guarda un 'pensamiento' simple para trazar decisiones/ideas del agente."""
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    text = (payload or {}).get("input") or (payload or {}).get("text")
    topic = (payload or {}).get("topic") or "general"
    tags = (payload or {}).get("tags") or []
    meta = (payload or {}).get("meta") or {}

    if not text:
        raise HTTPException(status_code=422, detail="Field 'input' (or 'text') is required")

    doc = {
        "kind": "thought",
        "text": str(text),
        "topic": str(topic),
        "tags": list(tags) if isinstance(tags, list) else [str(tags)],
        "meta": meta if isinstance(meta, dict) else {"_note": "meta not dict"},
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
    }
    fs = _fs()
    ref = fs.collection("agent_context").document()
    ref.set(doc)
    return {"ok": True, "id": ref.id, "stored": doc}

@app.get("/context")
def get_context(limit: int = Query(10, ge=1, le=100), topic: Optional[str] = None):
    """Devuelve contexto reciente (últimos N); filtrable por topic."""
    fs = _fs()
    q = fs.collection("agent_context")
    if topic:
        q = q.where("topic", "==", topic)
    # ordenar por ts descendente si está como string ISO
    q = q.order_by("ts", direction=firestore.Query.DESCENDING).limit(limit)
    docs = []
    for d in q.stream():
        data = d.to_dict()
        data["_id"] = d.id
        docs.append(data)
    return {"ok": True, "count": len(docs), "items": docs}


# === API Key auth middleware (refined) ===
EXEMPT_PATHS = {"/", "/health", "/openapi.json", "/docs", "/redoc", "/memory/test", "/__alive", "/__ops_import_status", "/__sha"}

@app.middleware("http")
async def require_api_key_mw(request: Request, call_next):
    if request.url.path in EXEMPT_PATHS:
        return await call_next(request)

    expected = os.getenv("API_KEY", "").strip()
    authz = request.headers.get("Authorization", "")
    bearer = authz.replace("Bearer ", "", 1).strip()
    supplied = (request.headers.get("X-API-Key") or bearer or "").strip()

    if not expected:
        response = await call_next(request)
        response.headers["X-Auth-Warning"] = "API_KEY not set on server"
        return response

    if not supplied or supplied != expected:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized: invalid API key"})

    return await call_next(request)


# === AUTO PLANNER MIN ===
def _fs():
    return firestore.Client()

def _iso_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# Crear un plan
@app.post("/auto/plan")
def auto_plan(payload: Dict[str, Any]):
    payload = payload or {}
    goal = payload.get("goal")
    constraints = payload.get("constraints", [])
    horizon = int(payload.get("horizon", 5))
    if not goal:
        raise HTTPException(status_code=400, detail="missing 'goal'")
    plan_id = uuid.uuid4().hex[:16]
    doc = {
        "plan_id": plan_id,
        "goal": goal,
        "constraints": constraints,
        "horizon": horizon,
        "status": "draft",
        "steps": [],
        "ts": _iso_now(),
    }
    _fs().collection("agent_plans").document(plan_id).set(doc)
    return { "ok": True, "plan_id": plan_id, "plan": doc }

# Ver un plan
@app.get("/auto/plan/{plan_id}")
def auto_plan_get(plan_id: str):
    snap = _fs().collection("agent_plans").document(plan_id).get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="plan not found")
    return { "ok": True, "plan": snap.to_dict() }

# Agregar un paso
@app.post("/auto/plan/{plan_id}/step")
def auto_plan_add_step(plan_id: str, payload: Dict[str, Any]):
    payload = payload or {}
    action = payload.get("action")
    params = payload.get("params", {})
    if not action:
        raise HTTPException(status_code=400, detail="missing 'action'")
    ref = _fs().collection("agent_plans").document(plan_id)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="plan not found")
    doc = snap.to_dict()
    step = {
        "id": uuid.uuid4().hex[:8],
        "action": action,
        "params": params,
        "ts": _iso_now(),
        "status": "pending",
    }
    doc.setdefault("steps", []).append(step)
    doc["ts"] = _iso_now()
    ref.set(doc)
    return { "ok": True, "step": step, "plan_id": plan_id }

# Listar últimos planes (orden por ts desc)
@app.get("/auto/list")
def auto_plan_list(limit: int = 10):
    q = (
        _fs().collection("agent_plans")
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(max(1, min(limit, 50)))
    )
    items = [d.to_dict() for d in q.stream()]
    return { "ok": True, "count": len(items), "items": items }


import hashlib

@app.get("/whoami")
async def whoami():
    # NO expone la API key; solo un hash para diagnóstico
    val = (os.getenv("API_KEY","")).strip().encode()
    h = hashlib.sha256(val).hexdigest()[:16]
    return {"service":"natacha-api", "sa": os.getenv("K_SERVICE","unknown"), "api_key_sha256_16": h}

try:
    pass
except ImportError:
    Limiter = None
    get_remote_address = None
    SlowAPIMiddleware = None
    RateLimitExceeded = Exception
from fastapi.responses import JSONResponse

limiter = (Limiter or (lambda *a, **k: None))(key_func=get_remote_address)
# app = FastAPI()  # DUPLICATE REMOVED
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests – please wait a moment."})


# --- mount memory_v2 (autopatch) ---
try:
    from routes.memory_v2 import router as memory_v2_router
    app.include_router(memory_v2_router)
except Exception as e:
    print('memory_v2 not mounted:', e)


@app.get('/health')
def health():
    import os, hashlib
    raw = (os.getenv('API_KEY','').strip()).encode()
    sig = (hashlib.sha256(raw).hexdigest()[:8]) if raw else ''
    mode = 'dev' if os.getenv('DEV_NOAUTH')=='1' else 'locked'
    return {'status':'ok','auth_mode':mode,'key_sig':sig}


# --- debug: expose rate_limit_mode in /health (no-op) ---
try:
    from fastapi import APIRouter
    import os
    _rl_flag = (os.getenv('RATE_LIMIT_DISABLE') == '1' or os.getenv('RATE_LIMIT_DISABLED') == '1')
    @app.get('/ops/rl')
    def rl_status():
        return {'rate_limit_disabled': _rl_flag}
except Exception as e:
    print('rl_status not mounted:', e)
