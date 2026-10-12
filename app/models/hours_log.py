from datetime import date
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class HoursLog(SQLModel, table=True):
    __tablename__ = "hours_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    log_date: date = Field(default_factory=date.today)
    activity_description: str = Field(min_length=1)
    hours: float = Field(default=0.0, ge=0.0)

    student: Mapped[Optional["User"]] = Relationship(
        back_populates="hours_logs",
        sa_relationship_kwargs={"foreign_keys": "[HoursLog.student_id]"},
    )
