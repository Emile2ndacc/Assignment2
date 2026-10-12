from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class StudentAppeal(SQLModel, table=True):
    __tablename__ = "student_appeal"

    id: Optional[int] = Field(default=None, primary_key=True)
    redemption_id: int = Field(foreign_key="redemption.id", unique=True, index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    award_id: int = Field(foreign_key="award.id", index=True)
    appeal_date: date = Field(default_factory=date.today)
    reason: str = Field(min_length=1)
    status: str = Field(default="pending", index=True)
    admin_id: Optional[int] = Field(default=None, foreign_key="user.id")
    admin_notes: Optional[str] = None
