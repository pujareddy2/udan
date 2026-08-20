"""
Reset script: Drops ALL tables and recreates them fresh with the correct schema.
Run this once when the schema has changed.
"""
from sqlmodel import SQLModel
from app.core.db import engine
import app.models  # noqa: F401 — registers all models

def reset():
    from sqlalchemy import text
    with engine.connect() as conn:
        print("Dropping all tables with CASCADE...")
        # Nuke and recreate the public schema — cleanest Postgres reset
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        conn.commit()
        print("All tables dropped.")

    print("Recreating tables with correct schema...")
    SQLModel.metadata.create_all(engine)
    print("All tables recreated successfully!")
    print("\nYou can now run: python -m data.load_data")

if __name__ == "__main__":
    reset()
