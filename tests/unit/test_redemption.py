from unittest.mock import Mock

import pytest

from app.models import Award, Redemption
from app.services.student_awards_service import StudentAwardsService


def make_service():
    service = StudentAwardsService(None)
    service.award_repo = Mock()
    service.hours_log_repo = Mock()
    service.redemption_repo = Mock()
    return service


def test_submit_redemption_creates_pending_request():
    service = make_service()
    award = Award(id=7, name="Movie Ticket", milestone_hours=20)
    redemption = Redemption(
        student_id=1,
        award_id=award.id,
        approval_status="pending",
        notes="Thanks",
    )
    service.award_repo.get_catalog_award_by_id.return_value = award
    service.hours_log_repo.get_total_hours.return_value = 20
    service.redemption_repo.get_latest_for_student_and_award.return_value = None
    service.redemption_repo.create.return_value = redemption

    result = service.request_redemption(1, award.id, "Thanks")

    assert result.approval_status == "pending"
    service.redemption_repo.create.assert_called_once_with(1, award.id, "Thanks")


def test_submit_redemption_rejects_unknown_award():
    service = make_service()
    service.award_repo.get_catalog_award_by_id.return_value = None

    with pytest.raises(ValueError, match="Award not found"):
        service.request_redemption(student_id=1, award_id=999)

    service.hours_log_repo.get_total_hours.assert_not_called()
    service.redemption_repo.create.assert_not_called()


def test_submit_redemption_requires_enough_hours():
    service = make_service()
    service.award_repo.get_catalog_award_by_id.return_value = Award(
        id=7,
        name="Movie Ticket",
        milestone_hours=20,
    )
    service.hours_log_repo.get_total_hours.return_value = 15

    with pytest.raises(ValueError, match="5.0 more volunteer hours"):
        service.request_redemption(student_id=1, award_id=7)

    service.redemption_repo.create.assert_not_called()


@pytest.mark.parametrize(
    ("status", "message"),
    [
        ("pending", "A pending redemption for this award already exists."),
        ("approved", "This award has already been redeemed and approved."),
    ],
)
def test_submit_redemption_rejects_pending_or_approved_duplicate(status, message):
    service = make_service()
    service.award_repo.get_catalog_award_by_id.return_value = Award(
        id=7,
        name="Movie Ticket",
        milestone_hours=20,
    )
    service.hours_log_repo.get_total_hours.return_value = 20
    service.redemption_repo.get_latest_for_student_and_award.return_value = Redemption(
        student_id=1,
        award_id=7,
        approval_status=status,
    )

    with pytest.raises(ValueError, match=message):
        service.request_redemption(student_id=1, award_id=7)

    service.redemption_repo.create.assert_not_called()


def test_submit_redemption_allows_retry_after_rejection():
    service = make_service()
    award = Award(id=7, name="Movie Ticket", milestone_hours=20)
    pending_redemption = Redemption(
        student_id=1,
        award_id=7,
        approval_status="pending",
    )
    service.award_repo.get_catalog_award_by_id.return_value = award
    service.hours_log_repo.get_total_hours.return_value = 20
    service.redemption_repo.get_latest_for_student_and_award.return_value = Redemption(
        student_id=1,
        award_id=7,
        approval_status="rejected",
    )
    service.redemption_repo.create.return_value = pending_redemption

    result = service.request_redemption(student_id=1, award_id=7)

    assert result.approval_status == "pending"
    service.redemption_repo.create.assert_called_once_with(1, 7, None)


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_admin_resolves_pending_redemption(decision):
    service = make_service()
    redemption = Redemption(
        id=12,
        student_id=1,
        award_id=7,
        approval_status="pending",
    )
    service.redemption_repo.get_by_id.return_value = redemption
    service.redemption_repo.update_status.return_value = redemption

    result = service.resolve_redemption(
        redemption_id=12,
        admin_id=2,
        decision=decision,
    )

    assert result is redemption
    service.redemption_repo.update_status.assert_called_once_with(12, decision, 2)
