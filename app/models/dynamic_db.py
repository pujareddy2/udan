from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class DynamicQuestionBank(SQLModel, table=True):
    __tablename__ = "dynamic_question_bank"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    field_name: str = Field(index=True)
    module: str = Field(index=True)
    question_text: str
    effort_penalty: int = Field(default=5) # 1-10
    is_active: bool = Field(default=True)

class UserQuestionAnswer(SQLModel, table=True):
    __tablename__ = "user_question_answers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    question_field: str = Field(index=True)
    answer_value: str
    
    answered_at: datetime = Field(default_factory=datetime.utcnow)

class QuestionConfidenceHistory(SQLModel, table=True):
    __tablename__ = "question_confidence_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    question_field: str = Field(index=True)
    
    confidence_gain: float = Field(default=0.0)
    opportunities_unlocked: int = Field(default=0)
    
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
