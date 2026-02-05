# learning/preferences.py
from typing import Dict
from memory.long_term import MemoryService

PREF_KEY = "preferences_v1"

def _load(user_id: int) -> Dict:
    raw = MemoryService.recall(user_id, "Profile", PREF_KEY)
    if not raw:
        return {"format": {"bullets": 0, "code": 0}, "verbosity": {"short": 0, "long": 0}}
    try:
        import json
        return json.loads(raw)
    except Exception:
        return {"format": {"bullets": 0, "code": 0}, "verbosity": {"short": 0, "long": 0}}

def _save(user_id: int, data: Dict):
    import json
    MemoryService.remember(user_id, "Profile", PREF_KEY, json.dumps(data))

def update_preferences_from_message(user_id: int, user_text: str):
    t = (user_text or "").lower()
    prefs = _load(user_id)

    if "step" in t or "bullet" in t or "\n-" in t:
        prefs["format"]["bullets"] += 1
    if "code" in t or "python" in t or "js" in t or "swift" in t:
        prefs["format"]["code"] += 1
    if "quick" in t or "short" in t:
        prefs["verbosity"]["short"] += 1
    if "detailed" in t or "deep" in t or "long" in t:
        prefs["verbosity"]["long"] += 1

    _save(user_id, prefs)

def get_preferences_hint(user_id: int) -> str:
    prefs = _load(user_id)
    bullets = prefs["format"]["bullets"]
    code = prefs["format"]["code"]
    short = prefs["verbosity"]["short"]
    long = prefs["verbosity"]["long"]

    hints = []
    if bullets > 2:
        hints.append("User often prefers structured bullet points.")
    if code > 2:
        hints.append("User often prefers code-first explanations.")
    if long > short and long > 2:
        hints.append("User tends to prefer detailed answers.")
    if short > long and short > 2:
        hints.append("User tends to prefer concise answers.")
    return "\n".join(hints) if hints else "No strong preference signals yet."
