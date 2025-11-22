"""
CONTRATO FUNCIONAL — semantic_memory_v2

Rol:
    Memoria semántica de largo plazo para Natacha.
    Guarda eventos (texto + tags + personas + timestamp + embedding)
    en Firestore. Provee búsqueda semántica simple y un mecanismo de
    resumen ejecutivo basado en LLM.

Garantías:
    - save_event() SIEMPRE guarda el evento, incluso si falla OpenAI
      (en cuyo caso embedding=[]).
    - search() nunca explota por embeddings inválidos o mal formados.
      Si la query no tiene embedding, devolvemos los items sin score.
    - summarize() nunca levanta excepción: siempre devuelve un dict
      con:
        {query, user_id, project, limit, context_preview,
         summary, model, error, items}

Firestore:
    Colección: semantic_memory_v2
    Campos mínimos:
        user_id: str
        project: str
        text: str
        tags: List[str]
        people: List[str]
        ts: float (epoch seconds)
        embedding: List[float] (puede estar vacía)

    Requiere índice compuesto:
        user_id ASC
        project ASC
        ts DESC

EndPoints HTTP:
    - POST /memory/v2/semantic/add
    - GET  /memory/v2/semantic/search
    - GET  /memory/v2/semantic/summary

Uso típico desde Python:
    from natacha_core import semantic_memory_v2

    semantic_memory_v2.save_event(
        user_id="sebastian",
        project="LLVC",
        text="Sophie de XCMG está demorada con las proformas...",
        tags=["xcmg", "sophie", "proformas", "llvc"],
        people=["sophie"],
    )

    items = semantic_memory_v2.search(
        user_id="sebastian",
        project="LLVC",
        q="proformas",
        limit=5,
    )

    summary = semantic_memory_v2.summarize(
        user_id="sebastian",
        project="LLVC",
        q="proformas",
        limit=5,
    )
"""
import os
import time
import math
from typing import List, Optional, Any, Dict

from google.cloud import firestore
from openai import OpenAI

COLLECTION = "semantic_memory_v2"

_firestore_client: Optional[firestore.Client] = None
_openai_client: Optional[OpenAI] = None


def _fs() -> firestore.Client:
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client


def _openai() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no configurada en el entorno")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def _embed_text(text: str) -> List[float]:
    client = _openai()
    if len(text) > 8000:
        text = text[:8000]

    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return list(res.data[0].embedding)


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0

    n = min(len(a), len(b))
    num = 0.0
    na = 0.0
    nb = 0.0

    for i in range(n):
        try:
            x = float(a[i]); y = float(b[i])
        except Exception:
            continue
        num += x * y
        na += x * x
        nb += y * y

    if na <= 0 or nb <= 0:
        return 0.0
    return num / math.sqrt(na * nb)


def _soft_decay(ts: float, now: float = None) -> float:
    """
    Frescura: decay suave basado en horas.
    1.0 = muy reciente, 0.0 = muy viejo.
    """
    if now is None:
        now = time.time()

    age_hours = max(0, (now - ts) / 3600)
    return math.exp(-age_hours / 72)  # ventana de ~3 días


def _tag_boost(query: str, tags: List[str]) -> float:
    """
    Si la query menciona un término contenido en los tags => boost leve.
    """
    if not query or not tags:
        return 0.0

    q = query.lower()
    score = 0.0
    for t in tags:
        if t.lower() in q:
            score += 0.10   # +10%
    return min(score, 0.30)  # máximo +30%


def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    if tags is None:
        tags = []
    if people is None:
        people = []

    try:
        embedding = _embed_text(text)
    except Exception:
        embedding = []

    doc = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags,
        "people": people,
        "ts": time.time(),
        "embedding": embedding,
    }

    _fs().collection(COLLECTION).add(doc)
    return {"status": "ok", "saved": doc}


def search(user_id=None, project=None, q=None, limit=50):
    db = _fs()
    query = db.collection(COLLECTION)

    if user_id:
        query = query.where("user_id", "==", user_id)
    if project:
        query = query.where("project", "==", project)

    limit = limit if isinstance(limit, int) and limit > 0 else 50

    docs = [
        d.to_dict()
        for d in query.order_by("ts", direction=firestore.Query.DESCENDING)
                     .limit(limit)
                     .stream()
    ]

    if not q:
        return docs

    try:
        q_vec = _embed_text(q)
    except Exception:
        return docs

    now = time.time()
    results = []
    for d in docs:
        emb = d.get("embedding") or []
        sim = 0.0
        if emb:
            try:
                sim = _cosine(q_vec, emb)
            except Exception:
                sim = 0.0

        frescura = _soft_decay(d.get("ts", now), now)
        tag_bonus = _tag_boost(q, d.get("tags") or [])

        # score híbrido
        score = (sim * 0.70) + (frescura * 0.20) + (tag_bonus * 0.10)

        dd = dict(d)
        dd["score"] = float(score)
        dd["sim"] = float(sim)
        dd["fresh"] = float(frescura)
        dd["tag_bonus"] = float(tag_bonus)
        results.append(dd)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def summarize(user_id=None, project=None, q=None, limit=5, max_tokens=256):
    items = search(user_id=user_id, project=project, q=q, limit=limit)

    lines = []
    for idx, item in enumerate(items, start=1):
        ts = item.get("ts")
        text = item.get("text", "")
        tags = item.get("tags") or []
        p = [f"[#{idx}]"]
        if ts:
            try:
                p.append(f"(ts={int(float(ts))})")
            except Exception:
                pass
        if tags:
            p.append(f"[{', '.join(tags)}]")
        header = " ".join(p)
        lines.append(f"{header}\n{text}")

    context_block = "\n\n".join(lines) if lines else "No hay recuerdos previos relevantes."

    prompt = (
        "Eres la memoria ejecutiva del asistente Natacha.\n\n"
        f"Consulta: {q}\n\n"
        "Recuerdos relevantes:\n"
        f"{context_block}\n\n"
        "Responde en español con:\n"
        "1) Un resumen breve y accionable.\n"
        "2) 3 puntos clave.\n"
        "3) Un próximo paso sugerido.\n"
    )

    model_used = "gpt-4o-mini"
    summary_text = ""
    error = None

    try:
        resp = _openai().chat.completions.create(
            model=model_used,
            messages=[{"role": "system", "content": "Eres memoria ejecutiva."},
                      {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        summary_text = resp.choices[0].message.content
    except Exception as e:
        error = str(e)
        combined = " ".join(i.get("text", "") for i in items)
        summary_text = combined[:600] if combined else "No hay recuerdos."

    return {
        "query": q,
        "summary": summary_text,
        "items": items,
        "error": error,
        "model": model_used,
        "context_preview": context_block,
    }
