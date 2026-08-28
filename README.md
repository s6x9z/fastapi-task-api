# FastAPI Task Management API

A lightweight RESTful Task API built with Python and FastAPI featuring JSON file persistence, Pydantic validation, and unit testing with Pytest.

## Features
- **CRUD Operations:** Complete endpoints for managing tasks (`GET`, `POST`, `PUT`, `DELETE`).
- **Data Validation:** Strict payload parsing using Pydantic models.
- **Persistence:** JSON file storage surviving application restarts.
- **Filtering:** Query parameter support for filtering completed tasks.
- **Testing:** Unit test suite using Pytest and FastAPI TestClient.

## Getting Started

### Prerequisites
- Python 3.10+
- Virtual Environment (`.venv`)

### Setup & Run
1. Activate virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1