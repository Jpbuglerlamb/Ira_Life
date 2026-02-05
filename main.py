#main.py
from fastapi import FastAPI
from api.routes import router as api_router
from api.profile.routes import router as profile_router
from workers import logger, reflection, reminder
from threading import Thread
import time
from dotenv import load_dotenv
import os
from memory.long_term import init_db, migrate_reminders_table

# Load environment variables
load_dotenv()
print("OPENAI_API_KEY loaded:", os.getenv("OPENAI_API_KEY") is not None)
init_db()
migrate_reminders_table()


def create_app() -> FastAPI:
    """Create and configure the FastAPI app."""
    app = FastAPI(title="AI Friend Backend", version="1.0.0")

    # Include routers
    app.include_router(api_router)
    app.include_router(profile_router)

    # Startup event for background workers
    @app.on_event("startup")
    def start_background_workers():
        logger.log_system_event("Background workers starting...")

        # -------------------------
        # Reminder checker loop
        # -------------------------
        def reminder_loop():
            from workers.reminder import execute_due_reminders, clear_expired_reminders
            while True:
                for user_id in range(1, 11):
                    execute_due_reminders(user_id)
                    clear_expired_reminders(user_id)
                time.sleep(30)

        Thread(target=reminder_loop, daemon=True).start()

        # -------------------------
        # Daily reflection loop
        # -------------------------
        def reflection_loop():
            while True:
                for user_id in range(1, 11):  # fetch user IDs dynamically in real app
                    reflection.reflect_user(user_id, "Secretary")
                time.sleep(60 * 60 * 24)  # run once every 24h

        Thread(target=reflection_loop, daemon=True).start()

        logger.log_system_event("Background workers started.")

    return app


# Initialize FastAPI app
app = create_app()