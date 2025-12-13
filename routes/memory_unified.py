from fastapi import APIRouter

from routes.memory_v2 import router as memory_v2_router
from routes.semantic_routes import router as semantic_router
from routes.embeddings_routes import router as embeddings_router
from routes.memory_engine_routes import router as memory_engine_router

router = APIRouter(prefix="/memory", tags=["memory-unified"])

# Memory v2 (core)
router.include_router(memory_v2_router)

# Semantic Memory
router.include_router(semantic_router)

# Embeddings layer
router.include_router(embeddings_router)

# Memory Engine (raw / consolidate / recent / context_bundle)
router.include_router(memory_engine_router)
