import pytest

from app.services.student_awards_service import StudentAwardsService


def test_log_hours_requires_description():
    service = StudentAwardsService(None)

    with pytest.raises(ValueError):
        service.log_hours(
            student_id=1,
            activity_description="",
            hours=2
        )