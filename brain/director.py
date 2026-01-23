from brain.responder import generate_response

def process_input(username, mode, message):
    """Wrapper for FastAPI or workers to call the AI responder."""
    return generate_response(username, mode, message)