from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

from app.models import *


# SQLite requires this
connect_args = (
    {"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {}
)

# Create Engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Shows SQL queries in terminal
    connect_args=connect_args
)


# Create Tables
def init_db():
    SQLModel.metadata.create_all(engine)


# Session Dependency
def get_session():
    with Session(engine) as session:
        yield session


# Run directly
if __name__ == "__main__":
    print("Database URL:", settings.DATABASE_URL)

    print("\nRegistered Tables:")
    print(SQLModel.metadata.tables.keys())

    init_db()

    print("\nDatabase initialized successfully!")