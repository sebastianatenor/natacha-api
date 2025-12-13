import time
from typing import List, Union, Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["internal"])

class EmbedRequest(BaseModel):
    texts: Union[str, List[str]]

@router.post("/__benchmark/embed")
def benchmark_embed(req: EmbedRequest) -> Dict[str, Any]:
    """
    Benchmark simple de embeddings:
    - Fuerza carga del modelo (si no está)
    - Genera embeddings
    - Devuelve timing + dimensión (sin devolver el vector completo)
    """
    from unified_core.semantic_core import get_semantic_core

    texts = req.texts
    if isinstance(texts, str):
        texts_list = [texts]
    else:
        texts_list = texts

    t0 = time.time()
    core = get_semantic_core()
    core.ensure_loaded()
    t_load = time.time()

    vecs = core.embed(texts_list)
    t_embed = time.time()

    # vecs puede ser np.ndarray o list; sacamos "dim" de forma robusta
    dim = None
    try:
        dim = int(getattr(vecs, "shape")[1])
    except Exception:
        try:
            dim = int(len(vecs[0]))
        except Exception:
            dim = None

    return {
        "status": "ok",
        "count_texts": len(texts_list),
        "dim": dim,
        "seconds_load_or_skip": round(t_load - t0, 4),
        "seconds_embed": round(t_embed - t_load, 4),
        "seconds_total": round(t_embed - t0, 4),
    }
