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
    """
    Cliente singleton de Firestore.
    """
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client


def _openai() -> OpenAI:
    """
    Cliente singleton de OpenAI.
    """
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Si esto pasa, preferimos explotar explícitamente
            raise RuntimeError("OPENAI_API_KEY no configurada en el entorno")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def _embed_text(text: str) -> List[float]:
    """
    Genera un embedding para el texto dado usando un modelo liviano.
    """
    client = _openai()
    # Defensa: por las dudas truncamos textos MUY largos
    if len(text) > 8000:
        text = text[:8000]

    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    # Siempre devolvemos una lista simple de floats
    return list(res.data[0].embedding)


def _cosine(a: List[float], b: List[float]) -> float:
    """
    Similitud coseno defensiva:
    - Si alguna norma es cero -> 0.0
    - Si las longitudes difieren -> se usa el mínimo.
    """
    if not a or not b:
        return 0.0

    n = min(len(a), len(b))
    num = 0.0
    norm_a = 0.0
    norm_b = 0.0

    for i in range(n):
        try:
            x = float(a[i])
            y = float(b[i])
        except (TypeError, ValueError, IndexError):
            # Si algo raro pasa con los tipos, ignoramos ese componente
            continue
        num += x * y
        norm_a += x * x
        norm_b += y * y

    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0

    return num / math.sqrt(norm_a * norm_b)


def save_event(user_id: str, project: str, text: str, tags=None, people=None):
    """
    Guarda un evento semántico, con embedding de OpenAI si está disponible.
    """
    if tags is None:
        tags = []
    if people is None:
        people = []

    embedding: List[float] = []
    try:
        embedding = _embed_text(text)
    except Exception:
        # Defensa: si algo falla con OpenAI, igual guardamos sin embedding
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


def search(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
):
    """
    Búsqueda semántica simple:
    - Filtra por user_id y project si vienen.
    - Si no hay q -> devuelve últimos eventos por ts.
    - Si hay q -> genera embedding de la query y rankea por similitud coseno.
    - Nunca explota por embeddings faltantes, mal formados o longitudes raras.

    IMPORTANTE: evitamos order_by() en Firestore para no requerir índices
    compuestos. Ordenamos por ts del lado de la aplicación.
    """
    db = _fs()
    query = db.collection(COLLECTION)

    if user_id:
        query = query.where("user_id", "==", user_id)
    if project:
        query = query.where("project", "==", project)

    # Leemos todos los documentos que matchean los filtros
    docs = [d.to_dict() for d in query.stream()]

    # Ordenamos por ts descendente del lado de Python
    def _ts_val(doc: Dict[str, Any]) -> float:
        try:
            return float(doc.get("ts", 0.0))
        except Exception:
            return 0.0

    docs.sort(key=_ts_val, reverse=True)

    # Defensa: aseguramos límite mínimo 1
    limit_value = limit if isinstance(limit, int) and limit > 0 else 50

    # Si no hay texto de búsqueda, devolvemos los últimos eventos tal cual
    if not q:
        return docs[:limit_value]

    # Intentamos generar embedding de la query; si falla, devolvemos fallback
    try:
        query_vec = _embed_text(q)
    except Exception:
        return docs[:limit_value]

    results: List[Dict[str, Any]] = []
    for d in docs:
        emb = d.get("embedding") or []
        score = 0.0
        if isinstance(emb, list) and emb:
            try:
                score = _cosine(query_vec, emb)
            except Exception:
                score = 0.0

        d_with_score = dict(d)
        d_with_score["score"] = float(score)
        results.append(d_with_score)

    # Ordenamos por score descendente
    results.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    # Respetamos el límite en la salida
    return results[:limit_value]


def summarize(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 5,
    max_tokens: int = 256,
) -> Dict[str, Any]:
    """
    Devuelve un resumen de los recuerdos más relevantes para la query dada.
    Nunca levanta excepción: si algo falla, devuelve un resumen fallback.
    """
    # Primero reutilizamos la búsqueda semántica
    items = search(user_id=user_id, project=project, q=q, limit=limit)

    # Armamos un bloque de contexto compacto
    lines = []
    for idx, item in enumerate(items, start=1):
        ts = item.get("ts")
        text = item.get("text", "")
        project_val = item.get("project") or ""
        tags = item.get("tags") or []
        tags_str = ", ".join(tags) if tags else ""
        parts = [f"[#{idx}]"]
        if project_val:
            parts.append(f"[{project_val}]")
        if ts:
            # timestamp puede venir como float o int; lo simplificamos
            try:
                ts_num = float(ts)
                parts.append(f"(ts={int(ts_num)})")
            except Exception:
                pass
        header = " ".join(parts)
        if tags_str:
            header = f"{header} [{tags_str}]"
        lines.append(f"{header}\n{text}")

    context_block = "\n\n".join(lines) if lines else "No hay recuerdos previos relevantes."

    # Prompt base para el modelo
    prompt = (
        "Eres la memoria de un asistente personal llamado Natacha, que ayuda a Sebastián con "
        "importaciones de maquinaria, coordinación con proveedores (como XCMG, Jamin, etc.) y "
        "la relación con sus clientes (Metalcon, Nubicom, etc.).\n\n"
        "Te paso fragmentos de recuerdos (eventos semánticos). Cada uno está numerado [#] y puede tener tags.\n\n"
        f"Consulta del usuario: {q or '(sin consulta explícita)'}\n\n"
        "Recuerdos:\n"
        f"{context_block}\n\n"
        "Responde en español con:\n"
        "1) Un resumen corto y accionable de la situación (2–3 frases).\n"
        "2) Hasta 3 puntos clave que Natacha debería tener presente.\n"
        "3) Si corresponde, una sugerencia concreta de próximo paso para Sebastián.\n"
    )

    # Llamada al modelo, con defensa total para no romper el endpoint
    summary_text = ""
    model_used = "gpt-4o-mini"
    error_message = None

    try:
        client = _openai()
        resp = client.chat.completions.create(
            model=model_used,
            messages=[
                {
                    "role": "system",
                    "content": "Eres una memoria ejecutiva para un asistente personal llamado Natacha."
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        summary_text = resp.choices[0].message.content
    except Exception as e:
        # Fallback: resumen básico concatenando textos
        error_message = str(e)
        joined = " ".join(item.get("text", "") for item in items)
        if not joined:
            summary_text = "No hay recuerdos almacenados para esta consulta."
        else:
            if len(joined) > 600:
                joined = joined[:600] + "..."
            summary_text = "Resumen aproximado (fallback sin modelo): " + joined

    return {
        "query": q,
        "user_id": user_id,
        "project": project,
        "limit": limit,
        "context_preview": context_block,
        "summary": summary_text,
        "model": model_used,
        "error": error_message,
        "items": items,
    }
