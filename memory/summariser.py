#memory/summariser.py
from memory.long_term import MemoryService, ReminderService
from memory.short_term import EphemeralService
from datetime import datetime

def summarize_memory(user_id, mode_name, max_entries=20):
    """
    Summarize a user's memory depending on the mode.

    Secretary: includes long-term memory, ephemeral context, and upcoming reminders.
    Build: includes long-term memory and ephemeral context (no reminders).
    VIP: includes long-term memory and ephemeral context (no reminders).
    """
    # -------------------------
    # 1. Long-term memory
    # -------------------------
    memory_items = MemoryService.list_memory(user_id, mode_name)
    if memory_items:
        memory_items = memory_items[-max_entries:]
        memory_text = "\n".join(f"{item['key']}: {item['value']}" for item in memory_items)
    else:
        memory_text = "No long-term memory yet."

    # -------------------------
    # 2. Ephemeral memory
    # -------------------------
    ephemeral_text = ""
    ephemeral = EphemeralService.get_context(user_id, summarize=True)
    if ephemeral:
        ephemeral_text = f"\nRecent conversation:\n{ephemeral}"

    # -------------------------
    # 3. Upcoming reminders (Secretary only)
    # -------------------------
    reminders_text = ""
    if mode_name == "Secretary":
        reminders = ReminderService.list_reminders(user_id)
        if reminders:
            upcoming = []
            for r in reminders:
                text = r[1]
                time_str = r[2] or "unspecified time"
                # Only include reminders that are in the future or have no time
                try:
                    if not r[2] or datetime.fromisoformat(r[2]) >= datetime.now():
                        upcoming.append(f"- {text} at {time_str}")
                except ValueError:
                    upcoming.append(f"- {text} at {time_str}")  # fallback for bad format
            if upcoming:
                reminders_text = "\nReminders:\n" + "\n".join(upcoming)

    # -------------------------
    # 4. Combine summaries
    # -------------------------
    summary = memory_text + ephemeral_text + reminders_text
    return summary.strip() or "No memory content available."