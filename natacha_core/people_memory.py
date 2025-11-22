from google.cloud import firestore
from typing import Dict, Any, Optional, List
from datetime import datetime

COLLECTION = "assistant_people"

def get_client():
    return firestore.Client()

def save_profile(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = get_client()
    ref = db.collection(COLLECTION).document(user_id)
    data["updated_at"] = datetime.utcnow().isoformat()
    ref.set(data, merge=True)
    return {"id": user_id, "profile": data}

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    db = get_client()
    doc = db.collection(COLLECTION).document(user_id).get()
    if doc.exists:
        return {"id": user_id, "profile": doc.to_dict()}
    return None

def search_profiles(limit: int = 20) -> List[Dict[str, Any]]:
    db = get_client()
    docs = db.collection(COLLECTION).limit(limit).stream()
    return [{"id": d.id, "profile": d.to_dict()} for d in docs]
