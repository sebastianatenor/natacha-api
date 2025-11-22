from google.cloud import firestore
from datetime import datetime
from typing import Dict, Any, List, Optional

COLLECTION = "assistant_projects"

def get_client():
    return firestore.Client()

def save_project(project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_client()
    ref = db.collection(COLLECTION).document(project_id)
    data["updated_at"] = datetime.utcnow().isoformat()
    ref.set(data, merge=True)
    return {"id": project_id, "project": data}

def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    db = get_client()
    doc = db.collection(COLLECTION).document(project_id).get()
    if doc.exists:
        return {"id": project_id, "project": doc.to_dict()}
    return None

def search_projects(limit: int = 20) -> List[Dict[str, Any]]:
    db = get_client()
    docs = db.collection(COLLECTION).limit(limit).stream()
    return [{"id": d.id, "project": d.to_dict()} for d in docs]
