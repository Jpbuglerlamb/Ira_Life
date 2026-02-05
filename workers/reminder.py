# workers/reminder.py
from memory.long_term import ReminderService
from datetime import datetime, timedelta

EXECUTION_WINDOW_SECONDS = 60
KEEP_AFTER_EXECUTION_DEFAULT = False

def _parse_time(time_str: str):
    try:
        return datetime.fromisoformat(time_str)
    except Exception:
        return None

def get_due_reminders(user_id: int):
    now = datetime.utcnow()
    due = []

    reminders = ReminderService.list_reminders(user_id)
    for r_id, text, time_str, status, sort_time in reminders:
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
    due_reminders = get_due_reminders(user_id)
    for r_id, text, reminder_time in due_reminders:
        print(f"[Reminder] User {user_id}: {text} @ {reminder_time.isoformat()}")
        if not keep_after_execution:
            ReminderService.delete_reminder(r_id)

def clear_expired_reminders(user_id: int, keep_after_execution: bool = KEEP_AFTER_EXECUTION_DEFAULT):
    if keep_after_execution:
        return

    now = datetime.utcnow()
    expiry_threshold = now - timedelta(hours=1)

    reminders = ReminderService.list_reminders(user_id)
    for r_id, text, time_str, status, sort_time in reminders:
        if not time_str:
            continue
        reminder_time = _parse_time(time_str)
        if reminder_time and reminder_time < expiry_threshold:
            ReminderService.delete_reminder(r_id)
