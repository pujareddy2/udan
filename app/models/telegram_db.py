from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TelegramConnection(SQLModel, table=True):
    """
    Stores the link between a UDAAN user and their Telegram account.
    Used by the Notification Engine to deliver personalized alerts.
    """
    __tablename__ = "telegram_connections"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    telegram_chat_id: str = Field(index=True)          # Telegram numeric chat ID as string
    telegram_username: Optional[str] = Field(default=None)  # @handle if available
    language: str = Field(default="en")                # "en", "hi", "te"
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction: Optional[datetime] = Field(default=None)


class TelegramBotLog(SQLModel, table=True):
    """Audit log of all messages sent to / received from Telegram users."""
    __tablename__ = "telegram_bot_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    telegram_chat_id: str = Field(index=True)
    direction: str = Field(default="outbound")  # "inbound" | "outbound"
    message_type: str = Field(default="text")   # "text" | "alert" | "command"
    content: str                                # Full message text
    command: Optional[str] = Field(default=None)  # e.g. "/start", "/help"
    created_at: datetime = Field(default_factory=datetime.utcnow)
