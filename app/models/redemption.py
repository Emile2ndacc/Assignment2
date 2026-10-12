from datetime import date
from typing import Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class Redemption(SQLModel, table=True):
    __tablename__ = "redemption"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    award_id: int = Field(foreign_key="award.id", index=True)
    redeemed_date: date = Field(default_factory=date.today)
    approval_status: str = Field(default="pending")
    notes: Optional[str] = None
    approved_by_admin_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    student: Mapped[Optional["User"]] = Relationship(
        back_populates="redemptions",
        sa_relationship_kwargs={"foreign_keys": "[Redemption.student_id]"},
    )
    award: Mapped[Optional["Award"]] = Relationship(back_populates="redemptions")
    approved_by_admin: Mapped[Optional["User"]] = Relationship(
        back_populates="reviewed_redemptions",
        sa_relationship_kwargs={"foreign_keys": "[Redemption.approved_by_admin_id]"},
    )
