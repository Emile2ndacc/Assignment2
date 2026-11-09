def test_log_hours_and_leaderboard_update(client, login, student):
    login("test_student", "test-password")

    response = client.post(
        "/app/log-hours",
        data={
            "activity_description": "Volunteered at event",
            "hours": "3.5",
            "log_date": "2026-11-09",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    response = client.get("/app/leaderboard")
    assert response.status_code == 200
    assert student.username in response.text
    assert "3.5h" in response.text
