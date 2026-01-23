# workers/logger.py

from datetime import datetime
from memory.short_term import EphemeralService

MAX_EPHEMERAL = 100  # Max messages per user to prevent memory bloat

def log_user_interaction(user_id: int, role: str, message: str):
    """
    Logs a message to ephemeral memory with timestamp.
    Also trims old messages if exceeding MAX_EPHEMERAL.
    """
    EphemeralService.log(user_id, role, message)

    # Trim ephemeral memory to max buffer
    if len(EphemeralService.ephemeral.get(user_id, [])) > MAX_EPHEMERAL:
        EphemeralService.ephemeral[user_id] = EphemeralService.ephemeral[user_id][-MAX_EPHEMERAL:]

    print(f"[{datetime.utcnow().isoformat()}] {role} (User {user_id}): {message}")


def log_system_event(event: str):
    """
    Logs a system-level event with timestamp.
    """
    print(f"[{datetime.utcnow().isoformat()}] SYSTEM: {event}")