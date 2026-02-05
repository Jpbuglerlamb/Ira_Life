# learning/topics.py
from typing import Dict, List, Tuple
from memory.long_term import MemoryService

TOPIC_KEY = "topics_v1"

TOPICS = {
    "ai_ml": ["ai", "ml", "model", "neural", "embedding", "dataset"],
    "backend": ["fastapi", "api", "uvicorn", "router", "endpoint", "sqlite"],
    "frontend": ["swiftui", "ios", "ui", "view", "xcode"],
    "raspi": ["raspberry", "pi", "ssh", "camera", "gpio"],
    "finance": ["money", "bank", "expense", "tax", "income"],
    "weather": ["rain", "weather", "forecast", "temperature", "wind"],
}

def _load(user_id: int) -> Dict[str, int]:
    raw = MemoryService.recall(user_id, "Profile", TOPIC_KEY)
    if not raw:
        return {}
    try:
        import json
        return json.loads(raw)
    except Exception:
        return {}

def _save(user_id: int, data: Dict[str, int]):
    import json
    MemoryService.remember(user_id, "Profile", TOPIC_KEY, json.dumps(data))

def update_topics(user_id: int, text: str):
    t = (text or "").lower()
    counts = _load(user_id)

    for topic, kws in TOPICS.items():
        if any(kw in t for kw in kws):
            counts[topic] = counts.get(topic, 0) + 1

    _save(user_id, counts)

def top_topics(user_id: int, n: int = 3) -> List[Tuple[str, int]]:
    counts = _load(user_id)
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
