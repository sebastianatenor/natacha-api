from google.cloud import firestore


def get_system_health(limit=20):
    db = firestore.Client()
    docs = (
        db.collection("system_health")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [d.to_dict() for d in docs]
