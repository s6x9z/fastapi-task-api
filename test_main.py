import os
import pytest
from fastapi.testclient import TestClient
import main
from main import app, init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Use an isolated temporary SQLite database for each test run."""
    db_file = tmp_path / "test_tasks.db"
    monkeypatch.setattr(main, "DB_FILE", str(db_file))
    init_db()
    yield


def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3 


def test_create_task():
    new_task = {"title": "Test with pytest", "done": False}
    response = client.post("/tasks", json=new_task)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test with pytest"
    assert data["done"] is False
    assert "id" in data


def test_update_task():
    updated_data = {"title": "Learn FastAPI - Updated", "done": True}
    response = client.put("/tasks/1", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Learn FastAPI - Updated"
    assert data["done"] is True


def test_delete_task():
    response = client.delete("/tasks/1")
    assert response.status_code == 204

    get_response = client.get("/tasks/1")
    assert get_response.status_code == 404