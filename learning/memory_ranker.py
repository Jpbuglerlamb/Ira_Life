# learning/memory_ranker.py
from typing import List, Dict, Any
import math
from learning.embedder import embed_text
from memory.vector_store import fetch_messages_with_embeddings

def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))

def top_k_relevant_messages(user_id: int, query_text: str, k: int = 8) -> List[Dict[str, Any]]:
    qvec = embed_text(query_text)
    if not qvec:
        return []

    candidates = fetch_messages_with_embeddings(user_id, limit=500)
    scored = []
    for item in candidates:
        s = _cosine(qvec, item["embedding"])
        if s > 0.2:
            scored.append((s, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": s, **it} for s, it in scored[:k]]

