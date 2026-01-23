#memory/short_term.py
EPHEMERAL_LIMIT = 12

class EphemeralService:
    ephemeral: dict[int, list[tuple[str, str]]] = {}

    @classmethod
    def log(cls, user_id: int, role: str, content: str):
        cls.ephemeral.setdefault(user_id, []).append((role, content))

    @classmethod
    def get_context(cls, user_id: int, summarize: bool = False) -> str:
        """
        Return full context or summarized context to prevent echoing.
        Summarize=True returns only AI messages or condensed history.
        """
        messages = cls.ephemeral.get(user_id, [])

        if summarize:
            # Echo-free: only AI messages or condensed summary
            ai_messages = [c for r, c in messages if r == "AI"]
            return "\n".join(ai_messages) if ai_messages else "No recent conversation."

        # Full raw context (for debugging / logs)
        return "\n".join(f"{r}: {c}" for r, c in messages)

    @classmethod
    def forget(cls, user_id):
        cls.ephemeral[user_id] = []