from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

tasks_db = []

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
def get_tasks():
    return {"tasks": tasks_db}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_id = len(tasks_db) + 1
    new_task = {
        "id": new_id,
        "title": task.title,
        "completed": task.completed
    }
    tasks_db.append(new_task)
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
            return task
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")