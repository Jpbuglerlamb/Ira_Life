# brain/responder.py

import os
import json
import openai
import dateparser
import dateparser.search
from datetime import datetime

from memory.short_term import EphemeralService
from memory.long_term import ReminderService
from memory.summariser import summarize_memory
from brain.persona import SYSTEM_PROMPTS, Mode
from brain.critic import review_response

openai.api_key = os.getenv("OPENAI_API_KEY")


# -----------------------------
# Pending reminder helpers
# -----------------------------
def _get_pending_reminder(user_id):
    for role, content in reversed(EphemeralService.ephemeral.get(user_id, [])):
        if role == "PendingReminder":
            try:
                return json.loads(content)
            except Exception:
                return None
    return None


def _clear_pending_reminder(user_id):
    EphemeralService.ephemeral[user_id] = [
        (r, c) for r, c in EphemeralService.ephemeral.get(user_id, [])
        if r != "PendingReminder"
    ]


# =========================================================
# Main responder
# =========================================================
def generate_response(user_id, mode, user_input: str) -> str:
    if isinstance(mode, dict):
        mode = Mode(**mode)

    EphemeralService.log(user_id, "User", user_input)
    lower_input = user_input.lower().strip()

    # =====================================================
    # SECRETARY MODE — REMINDERS ONLY
    # =====================================================
    if mode.name == "Secretary":
        # ---------- Pending confirmation ----------
        pending = _get_pending_reminder(user_id)
        if pending:
            normalized_input = lower_input.replace(",", "").replace(".", "").strip()
            positive_keywords = ["yes", "sure", "okay", "do it", "confirm", "go ahead", "set it"]
            negative_keywords = ["no", "cancel", "not now", "later"]

            if any(normalized_input.startswith(kw) or f" {kw} " in f" {normalized_input} " for kw in positive_keywords):
                ReminderService.add_reminder(user_id, pending["task"], pending["time"])
                _clear_pending_reminder(user_id)
                reply = f"Excellent — I’ve set a reminder for **{pending['task']}** at **{pending['display_time']}**."
                EphemeralService.log(user_id, "AI", reply)
                return reply

            if any(normalized_input.startswith(kw) or f" {kw} " in f" {normalized_input} " for kw in negative_keywords):
                _clear_pending_reminder(user_id)
                reply = "Okay, I won’t set that reminder."
                EphemeralService.log(user_id, "AI", reply)
                return reply

        # ---------- List reminders ----------
        if any(kw in lower_input for kw in ["list reminders", "show reminders", "my reminders"]):
            reminders = ReminderService.list_reminders(user_id)
            if not reminders:
                reply = "You don’t have any reminders yet."
            else:
                lines = []
                for r in reminders:
                    text = r[1]
                    time_str = r[2] or "unspecified time"
                    try:
                        if r[2] and datetime.fromisoformat(r[2]) < datetime.now():
                            time_str += " (overdue)"
                    except ValueError:
                        pass
                    lines.append(f"• {text} at {time_str}")
                reply = "Here are your reminders:\n" + "\n".join(lines)

            EphemeralService.log(user_id, "AI", reply)
            return reply

        # ---------- Create reminder ----------
        if any(kw in lower_input for kw in ["remind", "reminder"]):
            search_results = dateparser.search.search_dates(user_input, settings={"PREFER_DATES_FROM": "future"})
            if not search_results:
                reply = "When would you like me to remind you?"
                EphemeralService.log(user_id, "AI", reply)
                return reply

            matched_text, dt = max(search_results, key=lambda x: x[1])
            task = user_input.replace(matched_text, "").strip()
            for kw in ["remind me", "remind", "set a reminder", "can you"]:
                if task.lower().startswith(kw):
                    task = task[len(kw):].strip()
            task = " ".join(task.split()).strip(" .,")
            if not task:
                reply = "What would you like me to be reminded about?"
                EphemeralService.log(user_id, "AI", reply)
                return reply

            iso_time = dt.isoformat()
            display_time = dt.strftime("%A %d %B at %I:%M %p")
            EphemeralService.log(user_id, "PendingReminder", json.dumps({"task": task, "time": iso_time, "display_time": display_time}))

            reply = f"Just to confirm — would you like a reminder for **{task}** at **{display_time}**?"
            EphemeralService.log(user_id, "AI", reply)
            return reply

    # =====================================================
    # GPT FALLBACK — All modes chat naturally
    # =====================================================
    memory_summary = summarize_memory(user_id, mode.name)
    conversation_summary = EphemeralService.get_context(user_id, summarize=True)

    # Build messages for GPT
    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS.get(mode.name, "")},
        {"role": "system", "content": f"Memory Summary:\n{memory_summary}"},
        {"role": "system", "content": f"Conversation Summary:\n{conversation_summary}"},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            temperature=mode.temperature,
            max_tokens=mode.max_tokens
        )
        reply = response.choices[0].message.content
    except Exception:
        reply = "Sorry — something went wrong."

    # Optional: review response before sending
    try:
        reply = review_response(user_id, mode, reply)
    except Exception:
        pass

    EphemeralService.log(user_id, "AI", reply)
    return reply