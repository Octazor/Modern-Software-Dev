# TaskFlow — Project Task Tracker

A clean, production-structured Flask web application for tracking project tasks.
Built with Python, Flask, Jinja2 (SSR), Flask-SQLAlchemy, and SQLite.
No JavaScript — purely server-side rendered HTML and CSS.

---

## Folder Structure

```
task_tracker/
│
├── run.py                         # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
│
├── app/
│   ├── __init__.py                # Application factory (create_app)
│   │
│   ├── models/
│   │   ├── __init__.py            # Re-exports db + Task
│   │   └── task.py                # Task SQLAlchemy model + TaskStatus enum
│   │
│   ├── routes/
│   │   ├── __init__.py            # Re-exports tasks_bp Blueprint
│   │   └── tasks.py               # All CRUD routes + error handlers
│   │
│   └── templates/
│       ├── base.html              # Base layout (header, flash messages, footer)
│       ├── tasks/
│       │   ├── index.html         # Dashboard — lists all tasks with filter bar
│       │   └── form.html          # Shared create / edit form
│       └── errors/
│           ├── 404.html           # Not Found page
│           └── 500.html           # Internal Server Error page
│
├── tests/
│   ├── __init__.py
│   └── test_tasks.py              # Unit + integration tests (pytest)
│
└── instance/                      # Auto-created by Flask; holds tasks.db
```

---

## Prerequisites

- Python 3.11 or newer
- pip

---

## Setup Instructions

### 1. Clone / Download the Project

```bash
# If you received a zip, unzip it first, then:
cd task_tracker
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

| Platform | Command |
|----------|---------|
| macOS / Linux | `source .venv/bin/activate` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

You should see `(.venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY for production use.
```

For local development the defaults in `app/__init__.py` work without a `.env` file.

### 5. Initialize the Database

The database is created **automatically** on first run via `db.create_all()` inside
the application factory. You do **not** need to run any migration commands.

The SQLite database file will be created at:
```
instance/tasks.db
```

### 6. Run the Application

```bash
python run.py
```

Or, using the Flask CLI:

```bash
flask --app run run --debug
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

## Running Tests

Install the test dependency:

```bash
pip install pytest
```

Run the full test suite:

```bash
pytest tests/ -v
```

Tests use an **in-memory SQLite database** and never touch `instance/tasks.db`.

---

## Features

| Feature | Details |
|---------|---------|
| **Create** | Add a task with title, optional description, and status |
| **Read** | Dashboard lists all tasks; filter by status via query param |
| **Update** | Edit any field on an existing task |
| **Delete** | Remove a task with a confirmation prompt (pure HTML) |
| **Validation** | Title required, max 200 chars; status must be a valid enum value |
| **Flash messages** | Success/error feedback on every action |
| **404 / 500 pages** | Custom error pages for unknown task IDs or server errors |
| **No JavaScript** | All interaction handled by form POST + redirect (PRG pattern) |

---

## Architecture Notes

### Application Factory Pattern
`create_app()` in `app/__init__.py` initialises Flask, the database extension,
and registers blueprints. This makes the app fully testable — tests pass a
different `SQLALCHEMY_DATABASE_URI` without touching production data.

### Blueprint
All task routes live on `tasks_bp` (registered with no URL prefix).
Adding a future `/api/v1` REST blueprint is a one-liner in `create_app`.

### Validation Helper
`_validate_task_form()` in `routes/tasks.py` is a pure function — no Flask
context required — so it can be unit-tested directly without spinning up an
HTTP request.

### Model `to_dict()`
`Task.to_dict()` serialises a task to a plain dictionary. This is ready for
a future JSON API endpoint with zero changes to the model layer.

### PRG Pattern
Every successful POST redirects to GET (`redirect(url_for(...))`), preventing
duplicate form submissions on browser refresh.

---

## Extending the Application

### Add a new field (e.g. `due_date`)
1. Add the column to `app/models/task.py`.
2. Delete `instance/tasks.db` (dev only) or create an Alembic migration.
3. Add the form field to `templates/tasks/form.html`.
4. Read it in the `create` and `edit` route handlers.

### Add a REST API
1. Create `app/routes/api.py` with a new Blueprint and JSON responses.
2. Register it in `create_app` with `url_prefix="/api/v1"`.
3. Reuse `Task.to_dict()` for serialisation.

### Switch to PostgreSQL
Change `SQLALCHEMY_DATABASE_URI` in your `.env`:
```
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/taskflow
```
Install `psycopg2-binary` and run Alembic migrations. No model changes needed.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | SQLAlchemy ORM integration |
| SQLAlchemy | 2.0.30 | Database ORM |
| Werkzeug | 3.0.3 | WSGI utilities (bundled with Flask) |

---

## License

MIT — free to use and modify.
