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
from fastapi import FastAPI, Request, HTTPException, Query, HTTPException, Query, HTTPException, Query

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
from fastapi import FastAPI, Request, HTTPException, Query, HTTPException, Query, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, HTTPException, Query, HTTPException, Query, HTTPException, Query
from routes.health_routes import router as health_router
from routes.cog_routes import router as cog_router
from routes.actions_routes import router as actions_router
from routes.tasks_routes import router as tasks_router
from fastapi import FastAPI, Request, HTTPException, Query, HTTPException, Query, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os, hashlib, traceback
from routes.auto_routes import router as auto_router

# Configurar limitador global (por IP)
async def ratelimit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too Many Requests – please wait a moment."})

# Configurar limitador global (por IP)

from fastapi import FastAPI, Request, HTTPException, Query  # re-safe import (idempotente)
from fastapi.responses import JSONResponse

# === App canonical ===
app = FastAPI()

# === Routers existentes (ya importados arriba en el archivo) ===
# health_router, cog_router, actions_router, tasks_router, auto_router, CORS, etc.
try:
    app.include_router(health_router)
except Exception:
    pass
try:
    app.include_router(cog_router)
except Exception:
    pass
try:
    app.include_router(actions_router)
except Exception:
    pass
try:
    app.include_router(tasks_router)
except Exception:
    pass
try:
    app.add_middleware(CORSMiddleware,
        allow_origins=["https://dashboard.llvc-global.com","https://natacha-dashboard-422255208682.us-central1.run.app"],
        allow_methods=["*"], allow_headers=["*"])
except Exception:
    pass
try:
    app.include_router(auto_router)
except Exception:
    pass

# === Montaje ÚNICO de memory_v2 inmediatamente después ===
try:
    from routes.memory_v2 import router as memory_v2_router
    app.include_router(memory_v2_router)
except Exception as e:
    # no rompemos el boot: solo dejamos un check simple
    @app.get("/__mv2_check", include_in_schema=False)
    def __mv2_check_error():
        return {"mounted": False, "error": str(e)}
else:
    @app.get("/__mv2_check", include_in_schema=False)
    def __mv2_check_ok():
        try:
            from routes import memory_v2 as _mv2_mod
            pref = getattr(getattr(_mv2_mod, "router", None), "prefix", None)
            paths = [getattr(r, "path", "") for r in getattr(getattr(_mv2_mod, "router", None), "routes", [])]
            mounted = any(getattr(r, "path", "").startswith("/memory/v2") for r in getattr(app, "routes", []))
            return {"mounted": mounted, "prefix": pref, "router_routes": paths}
        except Exception as _inner:
            return {"mounted": False, "error": str(_inner)}

# === /__debug_routes simple ===
from fastapi.routing import APIRoute
@app.get("/__debug_routes")
def __debug_routes():
    items = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            items.append({
                "path": r.path,
                "methods": sorted(list(r.methods)),
                "in_schema": getattr(r, "include_in_schema", None)
            })
    return {"count": len(items), "routes": items}

# === Rate limit (sin duplicar) ===
try:
    limiter = (Limiter or (lambda *a, **k: None))(key_func=get_remote_address)
    app.state.limiter = limiter
    if SlowAPIMiddleware:
        app.add_middleware(SlowAPIMiddleware)
except Exception:
    pass

# handler único
try:
    @app.exception_handler(RateLimitExceeded)
    async def ratelimit_handler(request, exc):
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests – please wait a moment."})
except Exception:
    pass
