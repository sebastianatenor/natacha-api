# routes/memory_engine_alias.py

from fastapi import APIRouter

# Importamos el router legacy TAL CUAL está
from routes.memory_engine_routes import router as legacy_router

# Alias SIN prefix (hereda el del router legacy)
router = APIRouter(tags=["memory-engine-alias"])

# Re-exporta las rutas existentes
router.include_router(legacy_router)
