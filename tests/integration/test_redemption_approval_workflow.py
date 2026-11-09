from sqlmodel import select

from app.models import Redemption


def test_redemption_approval_workflow(
    client,
    login,
    student,
    admin,
    eligible_award,
    db_session,
):
    login("test_student", "test-password")
    response = client.post(
        f"/app/redeem/{eligible_award.id}",
        data={"notes": "Thank you"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    redemption = db_session.exec(
        select(Redemption).where(
            Redemption.student_id == student.id,
            Redemption.award_id == eligible_award.id,
        )
    ).one()
    assert redemption.approval_status == "pending"

    client.cookies.clear()
    login("test_admin", "test-password")
    response = client.post(
        f"/admin/redemptions/{redemption.id}/approved",
        follow_redirects=False,
    )
    assert response.status_code == 303

    db_session.refresh(redemption)
    assert redemption.approval_status == "approved"
    assert redemption.approved_by_admin_id == admin.id
