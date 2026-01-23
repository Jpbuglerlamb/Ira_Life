# brain/critic.py

from brain.persona import SYSTEM_PROMPTS

def review_response(user_id, mode, response_text):
    """
    Critic reviews the AI's response before sending it back.
    Returns the same text or a modified version.
    """
    # Example rule: If mode disallows NSFW, block keywords
    if not mode.NSFW_allowed:
        banned_words = ["explicit", "NSFW", "porn"]  # example
        for word in banned_words:
            response_text = response_text.replace(word, "[redacted]")

    # Could add more mode-specific checks here
    return response_text