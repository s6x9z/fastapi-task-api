from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

tasks_db = []

class TaskCreate(BaseModel):
    title: str
    completed: bool = False

class TaskResponse(BaseModel):
    id: int
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