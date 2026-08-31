import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

DB_FILE = "tasks.db"

def get_db_connection():
    """Returns a SQLite connection configured to return rows as dictionaries."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the tasks table if missing and seeds initial data if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        initial_tasks = [
            ("Learn FastAPI", 1),
            ("Build a CRUD API", 1),
            ("Connect SQLite Database", 0),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks
        )

    conn.commit()
    conn.close()

init_db()

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

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    """Fetch all tasks from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Fetch a single task by ID using parameterized SQL query."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return dict(row)


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate):
    """Insert a new task into SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, int(task.done)),
    )
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title, "done": task.done}


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    """Update an existing task in SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task.title, int(task.done), task_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    conn.close()
    return {"id": task_id, "title": task.title, "done": task.done}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Delete a task from SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)