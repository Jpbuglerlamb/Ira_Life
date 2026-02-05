# learning/context_builder.py
from typing import Dict, Any
from learning.intent import detect_intent
from learning.preferences import get_preferences_hint, update_preferences_from_message
from learning.topics import update_topics, top_topics
from learning.memory_ranker import top_k_relevant_messages

def build_learning_context(user_id: int, user_text: str) -> Dict[str, Any]:
    # Update trackers
    update_preferences_from_message(user_id, user_text)
    update_topics(user_id, user_text)

    intent, conf = detect_intent(user_text)
    prefs_hint = get_preferences_hint(user_id)
    topics = top_topics(user_id, n=3)
    memories = top_k_relevant_messages(user_id, user_text, k=8)

    return {
        "intent": {"label": intent, "confidence": conf},
        "preferences_hint": prefs_hint,
        "top_topics": topics,
        "retrieved_memories": memories,
    }

def format_learning_context(ctx: Dict[str, Any]) -> str:
    intent = ctx["intent"]
    topics = ctx["top_topics"]
    prefs = ctx["preferences_hint"]
    mem = ctx["retrieved_memories"]

    lines = []
    lines.append(f"Intent: {intent['label']} (confidence {intent['confidence']:.2f})")
    if topics:
        lines.append("Top topics: " + ", ".join([f"{t}({c})" for t, c in topics]))
    if prefs:
        lines.append("Preferences:\n" + prefs)
    if mem:
        lines.append("Relevant past messages:")
        for m in mem:
            lines.append(f"- ({m['role']}, score={m['score']:.2f}) {m['content']}")
    return "\n".join(lines)
