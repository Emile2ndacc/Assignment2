"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.award import Award
from app.models.hours_log import HoursLog
from app.models.redemption import Redemption
from app.models.student_appeal import StudentAppeal
from app.models.user import User

__all__ = ["User", "Award", "HoursLog", "Redemption", "StudentAppeal"]
