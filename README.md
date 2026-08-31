# FastAPI Task Management API

A lightweight RESTful Task API built with Python, FastAPI, and SQLite, featuring Pydantic validation and automated unit testing with Pytest.

## Features

* **CRUD Operations**: Complete RESTful endpoints for managing tasks (`GET`, `POST`, `PUT`, `DELETE`).
* **Database Persistence**: SQLite integration surviving application restarts.
* **Data Validation**: Strict payload parsing using Pydantic models.
* **Automated Testing**: Test suite built with Pytest and FastAPI's `TestClient` using isolated temporary test databases.

## Tech Stack

* **Language**: Python 3.12+
* **Framework**: FastAPI
* **Database**: SQLite3
* **Testing**: Pytest, HTTPX

## Getting Started

### 1. Set Up Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt