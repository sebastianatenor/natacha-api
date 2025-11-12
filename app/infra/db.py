import os
from pymongo import MongoClient
from app.infra.mongo_indexes import ensure_task_indexes

_client = None
_db = None
_tasks_col = None

def get_client():
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client = MongoClient(uri)
    return _client

def get_db():
    global _db
    if _db is None:
        name = os.getenv("MONGO_DB", "natacha")
        _db = get_client()[name]
    return _db

def get_tasks_col():
    """Devuelve la colección de tasks y garantiza índices."""
    global _tasks_col
    if _tasks_col is None:
        _tasks_col = get_db()["tasks"]
        ensure_task_indexes(_tasks_col)
    return _tasks_col
