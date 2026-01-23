# workers/reflection.py

from memory.long_term import MemoryService
from memory.short_term import EphemeralService
from datetime import datetime

def reflect_user(user_id: int, mode_name: str):
    """
    Summarize recent ephemeral conversation and store insights in long-term memory.
    """
    # Use echo-free summary to avoid storing repeated user messages
    recent = EphemeralService.get_context(user_id, summarize=True)
    if not recent:
        return "No recent conversation to reflect on."

    # Generate a unique key for the reflection
    summary_key = f"reflection_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    MemoryService.remember(user_id, mode_name, summary_key, recent)
    return f"Reflection stored as '{summary_key}'"