from fastapi import APIRouter
from ops.memory.recall import (
    recall_recent,
    recall_decisions,
    recall_by_subsystem,
)

router = APIRouter(tags=["memory"])


@router.get("/memory/recall/recent")
def recall_recent_api(limit: int = 20):
    return {
        "status": "ok",
        "events": recall_recent(limit),
    }


@router.get("/memory/recall/decisions")
def recall_decisions_api(limit: int = 10):
    return {
        "status": "ok",
        "events": recall_decisions(limit),
    }


@router.get("/memory/recall/{subsystem}")
def recall_subsystem_api(subsystem: str, limit: int = 10):
    return {
        "status": "ok",
        "events": recall_by_subsystem(subsystem, limit),
    }
