from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = ""


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    hours_logs: Mapped[list["HoursLog"]] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[HoursLog.student_id]"},
    )
    redemptions: Mapped[list["Redemption"]] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "[Redemption.student_id]"},
    )
    reviewed_redemptions: Mapped[list["Redemption"]] = Relationship(
        back_populates="approved_by_admin",
        sa_relationship_kwargs={"foreign_keys": "[Redemption.approved_by_admin_id]"},
    )