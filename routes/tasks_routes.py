from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Optional
from google.cloud import firestore
from google.oauth2 import service_account
import os

router = APIRouter(tags=["tasks"])

PROJECT_ID = os.getenv("GCP_PROJECT", "gen-lang-client-0363543020")

def get_db():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        creds = service_account.Credentials.from_service_account_file(cred_path)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    return firestore.Client(project=PROJECT_ID)

@router.post("/tasks/add")
def task_add(payload: dict):
    """Guarda una tarea pendiente en Firestore"""
    db = get_db()
    doc = {
        "title": payload.get("title", ""),
        "detail": payload.get("detail", ""),
        "project": payload.get("project", "general"),
        "channel": payload.get("channel", "chatgpt"),
        "due": payload.get("due", ""),
        "state": payload.get("state", "pending"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.collection("assistant_tasks").add(doc)
    return {"status": "ok", "stored": doc}

@router.get("/tasks/search")
def task_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    """Busca tareas filtradas por proyecto o estado"""
    db = get_db()
    q = db.collection("assistant_tasks").order_by(
        "created_at",
        direction=firestore.Query.DESCENDING,
    )
    docs = q.limit(200).stream()
    results = []
    for d in docs:
        item = d.to_dict()
        if project and item.get("project") != project:
            continue
        if state and item.get("state") != state:
            continue
        results.append({"id": d.id, **item})
        if len(results) >= limit:
            break
    return results
