from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
import models

app = FastAPI()

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    done: Optional[bool] = False


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    done: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True

@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    """Fetch all tasks from PostgreSQL database."""
    tasks = db.query(models.Task).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Fetch a single task by ID."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task in PostgreSQL database."""
    new_task = models.Task(title=task.title, done=task.done)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, task: TaskUpdate, db: Session = Depends(get_db)
):
    """Update an existing task in PostgreSQL database."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db_task.title = task.title
    db_task.done = task.done

    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task from PostgreSQL database."""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(db_task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)