import os
import pytest
from fastapi.testclient import TestClient
from main import app, FILE_PATH, load_tasks

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_test_db():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    load_tasks()
    yield
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    load_tasks()

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_get_task():
    post_res = client.post("/tasks", json={"title": "Test Task"})
    assert post_res.status_code == 201
    task = post_res.json()
    assert task["id"] == 1
    assert task["title"] == "Test Task"
    assert task["completed"] is False

    get_res = client.get(f"/tasks/{task['id']}")
    assert get_res.status_code == 200
    assert get_res.json() == task

def test_update_task():
    client.post("/tasks", json={"title": "Initial Task"})
    put_res = client.put("/tasks/1", json={"title": "Updated Task", "completed": True})
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Updated Task"
    assert put_res.json()["completed"] is True

def test_delete_task():
    client.post("/tasks", json={"title": "To Delete"})
    del_res = client.delete("/tasks/1")
    assert del_res.status_code == 204

    get_res = client.get("/tasks/1")
    assert get_res.status_code == 404

def test_query_filtering():
    client.post("/tasks", json={"title": "Task 1", "completed": False})
    client.post("/tasks", json={"title": "Task 2", "completed": True})

    res_completed = client.get("/tasks?completed=true")
    assert res_completed.status_code == 200
    assert len(res_completed.json()["tasks"]) == 1
    assert res_completed.json()["tasks"][0]["title"] == "Task 2"