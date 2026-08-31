# Task Management API

A FastAPI backend for task management, utilizing PostgreSQL in a Docker container, SQLAlchemy ORM, and Alembic for migrations.

## Setup Instructions

1. **Start the Database:**
   ```powershell
   docker run --name taskdb -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tasks -p 5432:5432 -d postgres