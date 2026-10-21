"""Single migration job, with a PostgreSQL advisory lock for concurrent invocations."""
import time
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from .db import engine

def main():
    for attempt in range(60):
        try:
            connection = engine.connect()
            break
        except Exception:
            if attempt == 59:
                raise RuntimeError("Database unavailable for migrations") from None
            time.sleep(2)
    with connection:
        connection.execute(text("SELECT pg_advisory_lock(210021)"))
        connection.commit()
        try:
            command.upgrade(Config("alembic.ini"), "head")
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(210021)"))
            connection.commit()

if __name__ == "__main__":
    main()
