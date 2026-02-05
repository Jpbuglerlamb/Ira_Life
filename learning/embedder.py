# learning/embedder.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

def embed_text(text: str) -> list[float]:
    text = (text or "").strip()
    if not text:
        return []

    try:
        resp = openai.embeddings.create(model=EMBED_MODEL, input=text)
        return resp.data[0].embedding
    except Exception:
        pass

    try:
        resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
        return resp["data"][0]["embedding"]
    except Exception:
        return []
