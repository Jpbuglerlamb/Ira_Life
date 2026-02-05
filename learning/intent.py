# learning/intent.py
from typing import Tuple

INTENTS = {
    "reminder": ["remind", "reminder", "set a reminder", "can you remind"],
    "debug": ["error", "traceback", "bug", "fix", "doesn't work", "not working"],
    "build": ["build", "create", "implement", "architecture", "design", "refactor"],
    "learn": ["learn", "course", "explain", "teach me", "how do i", "what is"],
    "chat": ["tell me", "thoughts", "why", "feel", "relationship", "life"],
}

def detect_intent(text: str) -> Tuple[str, float]:
    t = (text or "").lower()
    for name, kws in INTENTS.items():
        if any(kw in t for kw in kws):
            return name, 0.7
    return "chat", 0.4
