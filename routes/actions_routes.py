from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from firestore_client import get_db

router = APIRouter(tags=["actions"])


# ================================
# SCHEMAS
# ================================

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime


class MemoryAddPayload(BaseModel):
    user_id: str = Field(..., description="ID del usuario asociado a la memoria")
    note: str = Field(..., description="Contenido de la memoria")
    kind: Optional[str] = Field("general", description="Tipo de memoria")
    importance: Optional[str] = Field("normal", description="Importancia")
    source: Optional[str] = Field("actions", description="Origen")
    ttl_days: Optional[int] = Field(365, description="Días que debe vivir la memoria")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MemoryAddResponse(BaseModel):
    status: str
    memory_id: str
    stored_at: datetime


class TaskCreatePayload(BaseModel):
    title: str = Field(..., description="Título de la tarea")
    description: Optional[str] = Field(None, description="Descripción extendida")
    project: Optional[str] = Field("general", description="Proyecto o contexto")
    priority: Optional[str] = Field("normal", description="low | normal | high")
    status: Optional[str] = Field("open", description="open | in_progress | done")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskCreateResponse(BaseModel):
    status: str
    task_id: str
    stored_at: datetime


# ================================
# ROUTES
# ================================

@router.get("/health", response_model=HealthResponse)
def actions_health():
    return HealthResponse(
        status="ok",
        service="natacha-actions",
        timestamp=datetime.utcnow(),
    )


@router.post("/memory/add", response_model=MemoryAddResponse)
def memory_add(payload: MemoryAddPayload):
    db = get_db()

    expires_at = datetime.utcnow() + timedelta(days=payload.ttl_days)

    doc_ref = (
        db.collection("memory")
        .document(payload.user_id)
        .collection("items")
        .document()
    )

    data = {
        "note": payload.note,
        "kind": payload.kind,
        "importance": payload.importance,
        "source": payload.source,
        "metadata": payload.metadata,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
    }

    doc_ref.set(data)

    return MemoryAddResponse(
        status="saved",
        memory_id=doc_ref.id,
        stored_at=datetime.utcnow(),
    )


@router.post("/tasks/create", response_model=TaskCreateResponse)
def tasks_create(payload: TaskCreatePayload):
    db = get_db()

    project = payload.project or "general"

    doc_ref = (
        db.collection("tasks")
        .document(project)
        .collection("items")
        .document()
    )

    data = {
        "title": payload.title,
        "description": payload.description,
        "project": project,
        "priority": payload.priority,
        "status": payload.status,
        "metadata": payload.metadata,
        "created_at": datetime.utcnow(),
    }

    doc_ref.set(data)

    return TaskCreateResponse(
        status="created",
        task_id=doc_ref.id,
        stored_at=datetime.utcnow(),
    )
