# TaskTrack — Project Task Tracker

A clean, full-featured **Project Task Tracker** built with Python, Flask, Jinja2, and SQLite.  
No frontend JavaScript. Pure SSR with HTML & CSS.

---

## Folder Structure

```
task_tracker/
├── app.py                        # Entry point & error handlers
├── requirements.txt
├── .gitignore
│
├── app/
│   ├── __init__.py               # Application factory (create_app)
│   ├── extensions.py             # Shared Flask extensions (db)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py               # Task model + TaskStatus enum
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py              # Tasks blueprint (all CRUD routes)
│   │
│   └── templates/
│       ├── base.html             # Layout with nav, flash messages, CSS
│       ├── errors/
│       │   ├── 404.html
│       │   └── 500.html
│       └── tasks/
│           ├── dashboard.html    # Task list + stats + filters
│           └── form.html         # Shared create / edit form
│
└── tests/
    ├── __init__.py
    └── test_tasks.py             # Full pytest unit test suite
```

---

## Prerequisites

- Python **3.11+**
- pip

---

## Setup & Run

### 1 — Clone / download the project

```bash
# If using git:
git clone <your-repo-url>
cd task_tracker

# Or just cd into the extracted folder:
cd task_tracker
```

### 2 — Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Database initialization

The database is created **automatically** on first run via `db.create_all()` inside the application factory.  
No migration commands are needed. SQLite will create an `instance/tasks.db` file on startup.

### 5 — Run the development server

```bash
flask --app app run --debug
```

Or equivalently:

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## Running the Tests

The test suite uses **pytest** and an in-memory SQLite database — no real DB file is touched.

```bash
pip install pytest          # if not already installed
pytest tests/ -v
```

Expected output:

```
tests/test_tasks.py::TestTaskModel::test_all_statuses_returns_three_values  PASSED
tests/test_tasks.py::TestTaskModel::test_task_defaults_to_pending           PASSED
tests/test_tasks.py::TestTaskModel::test_task_repr                          PASSED
tests/test_tasks.py::TestDashboard::test_dashboard_loads                    PASSED
...
26 passed in 0.42s
```

---

## Application Routes

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/`                     | Dashboard — list tasks   |
| GET    | `/tasks/new`            | New task form            |
| POST   | `/tasks/new`            | Create task              |
| GET    | `/tasks/<id>/edit`      | Edit task form           |
| POST   | `/tasks/<id>/edit`      | Update task              |
| POST   | `/tasks/<id>/delete`    | Delete task              |

---

## Design Decisions & Architecture Notes

### Application Factory (`create_app`)
Using the factory pattern makes the app fully testable — tests pass in a custom config dict (e.g. `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`) without touching real data or environment variables.

### Blueprints
All task routes live in `app/routes/tasks.py` as a Blueprint. Adding new resources (e.g. Projects, Users) simply means registering a new Blueprint — no changes to existing code.

### Extensions module
`app/extensions.py` holds the `db = SQLAlchemy()` instance. This breaks the circular import that would occur if `db` were defined inside `app/__init__.py` and then imported by models.

### Models
`TaskStatus` is a `str` enum, so:
- SQLAlchemy stores human-readable strings (`"Pending"`, `"In Progress"`, `"Completed"`)
- Jinja2 templates can compare `task.status == "Pending"` directly
- The API surface is type-safe for future use

### Validation
Backend validation lives in `_validate_task_form()` inside the routes file — a pure function that takes raw strings and returns a list of error messages. This makes it trivially unit-testable and completely decoupled from Flask's request context.

### Flash Messages
Success and error notifications use Flask's built-in `flash()` + `get_flashed_messages()` — no JavaScript required. Messages are styled with a colored left border (green = success, red = error).

### No JavaScript
All interactions use plain HTML `<form>` elements with `method="POST"`. The delete confirmation uses the HTML `onsubmit="return confirm(...)"` attribute — the only inline JS in the project, and fully graceful-degradation-safe (browsers without JS will still submit the form).

---

## Production Checklist

Before deploying:

1. **Change `SECRET_KEY`** — set a long random string via environment variable:
   ```python
   app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
   ```

2. **Switch to a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn "app:app" --workers 4
   ```

3. **Use PostgreSQL** for multi-process deployments — update `SQLALCHEMY_DATABASE_URI`.

4. **Add Flask-Migrate** (`flask-migrate`) if you need schema migrations.

5. **Add CSRF protection** — install `Flask-WTF` and enable `CSRFProtect(app)`.

---

## Extending the App

| Goal | What to do |
|------|-----------|
| Add a `priority` field | Add column to `Task`, create Alembic migration, update form template |
| Add user authentication | Add a `User` model, use Flask-Login, scope tasks by `user_id` |
| Expose a REST API | Add an `app/routes/api.py` blueprint returning `jsonify()` responses |
| Add due dates | Add `due_date` DateTimeColumn, add date input to form template |
| Write integration tests | Use `pytest-flask` and the existing `client` fixture pattern |
