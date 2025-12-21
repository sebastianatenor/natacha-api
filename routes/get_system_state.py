from fastapi import APIRouter
from routes.health import health

router = APIRouter(tags=["Compatibility"])

@router.get("/get_system_state")
def get_system_state():
    # Alias de compatibilidad → health
    return health()

