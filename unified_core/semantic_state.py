# unified_core/semantic_state.py

from threading import Lock

_lock = Lock()
_semantic_loaded = False
_last_error = None

def mark_loaded():
    global _semantic_loaded, _last_error
    with _lock:
        _semantic_loaded = True
        _last_error = None

def mark_error(err: str):
    global _semantic_loaded, _last_error
    with _lock:
        _semantic_loaded = False
        _last_error = err

def is_loaded() -> bool:
    return _semantic_loaded

def last_error():
    return _last_error
