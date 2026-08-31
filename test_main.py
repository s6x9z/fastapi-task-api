import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
import models

from database import DATABASE_URL

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for a test function."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Override get_db dependency to use test database transaction session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_check_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Pytest Task", "done": False})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Pytest Task"
    assert data["done"] is False
    assert "id" in data


def test_get_tasks(client):
    client.post("/tasks", json={"title": "Task 1", "done": False})
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_single_task(client):
    create_res = client.post("/tasks", json={"title": "Fetch Me", "done": False})
    task_id = create_res.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fetch Me"


def test_update_task(client):
    create_res = client.post("/tasks", json={"title": "Old Title", "done": False})
    task_id = create_res.json()["id"]

    response = client.put(
        f"/tasks/{task_id}", json={"title": "New Title", "done": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["done"] is True


def test_delete_task(client):
    create_res = client.post("/tasks", json={"title": "To Delete", "done": False})
    task_id = create_res.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404