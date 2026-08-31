import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

DB_FILE = "tasks.db"


# --- Database Helpers ---
def get_db_connection():
    """Returns a SQLite connection configured to return rows as dictionaries."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the tasks table if missing and seeds initial data if table is empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # 2. Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # 3. Seed 3 example tasks only if count is 0
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


# Initialize DB when the script loads
init_db()


# --- Pydantic Models ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    done: Optional[bool] = False


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool


# Temporary GET /tasks endpoint for testing Stage 0
@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]