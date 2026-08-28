import json
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()

FILE_PATH = "tasks.json"
tasks_db = []


def load_tasks():
    """Load tasks from JSON file on startup."""
    global tasks_db
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r") as f:
                tasks_db = json.load(f)
        except json.JSONDecodeError:
            tasks_db = []
    else:
        tasks_db = []

def save_tasks():
    """Write current tasks list to JSON file."""
    with open(FILE_PATH, "w") as f:
        json.dump(tasks_db, f, indent=4)

load_tasks()

class TaskCreate(BaseModel):
    title: str
    completed: bool = False

class TaskUpdate(BaseModel):
    title: str
    completed: bool

@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(completed: Optional[bool] = None):
    if completed is not None:
        filtered_tasks = [t for t in tasks_db if t["completed"] == completed]
        return {"tasks": filtered_tasks}
    return {"tasks": tasks_db}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
    new_task = {
        "id": new_id,
        "title": task.title,
        "completed": task.completed
    }
    tasks_db.append(new_task)
    save_tasks()
    return new_task

@app.get("/tasks/{task_id}")
def get_task_by_id(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: TaskUpdate):
    for task in tasks_db:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["completed"] = updated_task.completed
            save_tasks()
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(index)
            save_tasks()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")