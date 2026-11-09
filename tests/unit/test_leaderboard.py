from app.services.student_awards_service import StudentAwardsService


def test_service_has_leaderboard():
    service = StudentAwardsService(None)

    assert hasattr(service, "get_leaderboard")