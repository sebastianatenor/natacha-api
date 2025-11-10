from typing import List, Optional
from pydantic import BaseModel, Field

class MemoryItem(BaseModel):
    text: str = Field(..., min_length=1)
    tags: Optional[List[str]] = None
    meta: Optional[dict] = None
    embedding: Optional[List[float]] = None  # opcional, para semántica

class MemoryStoreRequest(BaseModel):
    items: List[MemoryItem]

class MemoryQuery(BaseModel):
    query: str
    top_k: int = 10
    tags: Optional[List[str]] = None
    use_semantic: bool = True
