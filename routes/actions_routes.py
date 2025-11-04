from fastapi import APIRouter

router = APIRouter(prefix="/actions", tags=["actions"])

@router.get("/catalog", summary="List available agent actions")
def actions_catalog():
    return {
        "actions": [
            {"name": "tasks.add", "endpoint": "/tasks/add", "method": "POST"},
            {"name": "tasks.list", "endpoint": "/tasks/list", "method": "GET"},
        ]
    }
