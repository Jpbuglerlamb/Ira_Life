# workers/reminder.py

from memory.long_term import ReminderService
from datetime import datetime, timedelta

# How close to the reminder time we allow execution
EXECUTION_WINDOW_SECONDS = 60

# Whether reminders are deleted after firing
KEEP_AFTER_EXECUTION_DEFAULT = False


def _parse_time(time_str: str) -> datetime | None:
    """Safely parse ISO time."""
    try:
        return datetime.fromisoformat(time_str)
    except Exception:
        return None


def get_due_reminders(user_id: int):
    """
    Returns reminders that should fire now.
    A reminder is due if its scheduled time is within the execution window.
    """
    now = datetime.utcnow()
    due = []

    reminders = ReminderService.list_reminders(user_id)

    for r_id, text, time_str in reminders:
        if not time_str:
            continue

        reminder_time = _parse_time(time_str)
        if not reminder_time:
            continue

        delta = (reminder_time - now).total_seconds()

        if 0 <= delta <= EXECUTION_WINDOW_SECONDS:
            due.append((r_id, text, reminder_time))

    return due


def execute_due_reminders(user_id: int, keep_after_execution: bool = KEEP_AFTER_EXECUTION_DEFAULT):
    """
    Executes all reminders that are due now.
    """
    due_reminders = get_due_reminders(user_id)

    for r_id, text, reminder_time in due_reminders:
        # 🔔 Trigger reminder action (notification, UI event, etc.)
        print(f"[Reminder] User {user_id}: {text} @ {reminder_time.isoformat()}")

        # 🧹 Cleanup
        if not keep_after_execution:
            ReminderService.delete_reminder(user_id, r_id)


def clear_expired_reminders(user_id: int, keep_after_execution: bool = KEEP_AFTER_EXECUTION_DEFAULT):
    """
    Removes reminders that are far in the past.
    This prevents DB clutter if execution was missed.
    """
    if keep_after_execution:
        return

    now = datetime.utcnow()
    expiry_threshold = now - timedelta(hours=1)

    reminders = ReminderService.list_reminders(user_id)

    for r_id, _, time_str in reminders:
        if not time_str:
            continue

        reminder_time = _parse_time(time_str)
        if reminder_time and reminder_time < expiry_threshold:
            ReminderService.delete_reminder(user_id, r_id)