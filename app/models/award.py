from typing import Optional

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class Award(SQLModel, table=True):
    __tablename__ = "award"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    milestone_hours: float = Field(default=0.0, ge=0.0)
    description: Optional[str] = None

    redemptions: Mapped[list["Redemption"]] = Relationship(back_populates="award")
