from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.models import Award, HoursLog, User
from app.utilities.security import encrypt_password


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_engine, monkeypatch):
    def override_get_session():
        with Session(test_engine) as session:
            yield session

    monkeypatch.setitem(app.dependency_overrides, get_session, override_get_session)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def login(client):
    def authenticate(username: str, password: str):
        response = client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )
        assert response.status_code == 303
        return response

    return authenticate


@pytest.fixture
def student(db_session):
    user = User(
        username="test_student",
        email="test_student@example.com",
        password=encrypt_password("test-password"),
        role="regular_user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin(db_session):
    user = User(
        username="test_admin",
        email="test_admin@example.com",
        password=encrypt_password("test-password"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def eligible_award(db_session, student):
    award = Award(name="Movie Ticket", milestone_hours=2.0)
    db_session.add(award)
    db_session.commit()
    db_session.refresh(award)
    db_session.add(
        HoursLog(
            student_id=student.id,
            log_date=date.today(),
            activity_description="Test volunteer activity",
            hours=3.5,
        )
    )
    db_session.commit()
    return award
