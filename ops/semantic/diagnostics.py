from ops.semantic.state import SEMANTIC_STATE


def semantic_status():
    return {
        "loaded": SEMANTIC_STATE.loaded,
        "model": SEMANTIC_STATE.model_name,
        "hf_token_present": SEMANTIC_STATE.hf_token_present,
        "embedding_dim": SEMANTIC_STATE.embedding_dim,
    }
