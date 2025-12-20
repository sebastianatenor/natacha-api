from pathlib import Path
import os

# Local (Cloud Run writable)
VECTOR_INDEX_LOCAL = Path(
    os.getenv("NATACHA_VECTOR_INDEX_LOCAL", "/tmp/vector_index.faiss")
)

VECTOR_META_LOCAL = Path(
    os.getenv("NATACHA_VECTOR_META_LOCAL", "/tmp/vector_meta.jsonl")
)

# GCS
GCS_BUCKET = os.getenv("NATACHA_MEMORY_BUCKET", "natacha-memory-store")
VECTOR_INDEX_BLOB = "vector_index.faiss"
VECTOR_META_BLOB = "vector_meta.jsonl"
