# ops/semantic/embeddings.py
from sentence_transformers import SentenceTransformer


def load_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return SentenceTransformer(model_name)


def embed(texts, model):
    return model.encode(texts, convert_to_tensor=False)
