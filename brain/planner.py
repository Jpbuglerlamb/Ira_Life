# brain/planner.py

"""
Planner responsibility (IMPORTANT):
- The planner NEVER parses natural language deeply
- The planner NEVER creates reminders
- The planner ONLY describes *what kind of action* the AI should take next

All intelligence, parsing, confirmation, and persistence happens in responder.py
"""

from memory.short_term import EphemeralService


def generate_plan(user_id, mode, message):
    """
    Generates high-level intent steps for the responder.
    No side effects. No database writes.
    """
    steps = []

    # Planner only applies to Secretary mode
    if mode.name != "Secretary":
        return steps

    message_lower = message.lower()

    # Detect reminder intent ONLY (no parsing, no guessing)
    reminder_keywords = ["remind", "reminder", "set a reminder", "can you remind"]

    if any(kw in message_lower for kw in reminder_keywords):
        steps.append("User intends to create a reminder. Ask for confirmation and missing details.")
    else:
        steps.append("No actionable planning required. Respond conversationally.")

    # Log planner output for traceability/debugging
    EphemeralService.log(user_id, "Planner", str(steps))

    return steps