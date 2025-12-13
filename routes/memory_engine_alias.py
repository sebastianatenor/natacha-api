# routes/memory_engine_alias.py

from fastapi import APIRouter

# Importamos el router ya existente (legacy pero funcional)
from routes.memory_engine_routes import router as legacy_router

# Creamos un router limpio
router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])

# Reutilizamos todas las rutas existentes
router.include_router(legacy_router)
