"""
Unit & Integration Tests — Task Tracker
----------------------------------------
Run with:  pytest tests/ -v

Covers:
  - Validation helper (_validate_task_form)
  - Task model helpers (to_dict, __repr__)
  - All CRUD route integration tests (via Flask test client)
  - Flash message propagation
  - 404 handling for unknown task IDs
"""

import pytest
from app import create_app
from app.models import db as _db, Task, TaskStatus
from app.routes.tasks import _validate_task_form


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def app():
    """Isolated Flask app with in-memory SQLite for each test."""
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_task(app):
    """Create and return a persisted Task for use in tests."""
    with app.app_context():
        task = Task(
            title="Write unit tests",
            description="Cover all CRUD routes",
            status=TaskStatus.PENDING.value,
        )
        _db.session.add(task)
        _db.session.commit()
        # Detach from session so callers can read attributes safely
        _db.session.refresh(task)
        return task.id  # Return just the ID to avoid detached-instance issues


# ── Unit tests: validation helper ───────────────────────────────────────────

class TestValidation:
    def test_valid_input(self):
        errors = _validate_task_form("My task", TaskStatus.PENDING.value)
        assert errors == []

    def test_empty_title(self):
        errors = _validate_task_form("", TaskStatus.PENDING.value)
        assert any("Title" in e for e in errors)

    def test_whitespace_only_title(self):
        errors = _validate_task_form("   ", TaskStatus.PENDING.value)
        assert any("Title" in e for e in errors)

    def test_title_too_long(self):
        errors = _validate_task_form("x" * 201, TaskStatus.PENDING.value)
        assert any("200" in e for e in errors)

    def test_invalid_status(self):
        errors = _validate_task_form("Valid title", "NotAStatus")
        assert any("status" in e.lower() for e in errors)

    def test_all_valid_statuses(self):
        for status in TaskStatus.values():
            assert _validate_task_form("Title", status) == []


# ── Unit tests: Task model ───────────────────────────────────────────────────

class TestTaskModel:
    def test_to_dict_keys(self, app, sample_task):
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            d = task.to_dict()
            assert set(d.keys()) == {"id", "title", "description", "status",
                                     "created_at", "updated_at"}

    def test_repr(self, app, sample_task):
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            assert "Task" in repr(task)
            assert str(task.id) in repr(task)

    def test_status_enum_values(self):
        values = TaskStatus.values()
        assert "Pending" in values
        assert "In Progress" in values
        assert "Completed" in values


# ── Integration tests: Dashboard ────────────────────────────────────────────

class TestDashboard:
    def test_empty_dashboard(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"No tasks yet" in resp.data

    def test_dashboard_lists_tasks(self, client, app, sample_task):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Write unit tests" in resp.data

    def test_filter_by_status(self, client, app, sample_task):
        resp = client.get("/?status=Pending")
        assert resp.status_code == 200
        assert b"Write unit tests" in resp.data

    def test_filter_excludes_other_status(self, client, app, sample_task):
        resp = client.get("/?status=Completed")
        assert resp.status_code == 200
        assert b"Write unit tests" not in resp.data


# ── Integration tests: Create ────────────────────────────────────────────────

class TestCreate:
    def test_get_create_form(self, client):
        resp = client.get("/tasks/new")
        assert resp.status_code == 200
        assert b"Create" in resp.data

    def test_create_valid_task(self, client, app):
        resp = client.post("/tasks/new", data={
            "title": "Integration test task",
            "description": "Created by pytest",
            "status": "Pending",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Integration test task" in resp.data
        assert b"created successfully" in resp.data

    def test_create_empty_title_returns_422(self, client):
        resp = client.post("/tasks/new", data={
            "title": "",
            "description": "No title",
            "status": "Pending",
        })
        assert resp.status_code == 422
        assert b"Title" in resp.data

    def test_create_persists_to_db(self, client, app):
        client.post("/tasks/new", data={
            "title": "Persistence check",
            "description": "",
            "status": "In Progress",
        })
        with app.app_context():
            task = _db.session.scalars(
                _db.select(Task).where(Task.title == "Persistence check")
            ).first()
            assert task is not None
            assert task.status == "In Progress"


# ── Integration tests: Edit ──────────────────────────────────────────────────

class TestEdit:
    def test_get_edit_form(self, client, app, sample_task):
        resp = client.get(f"/tasks/{sample_task}/edit")
        assert resp.status_code == 200
        assert b"Write unit tests" in resp.data

    def test_edit_unknown_task_returns_404(self, client):
        resp = client.get("/tasks/99999/edit")
        assert resp.status_code == 404

    def test_edit_updates_task(self, client, app, sample_task):
        resp = client.post(f"/tasks/{sample_task}/edit", data={
            "title": "Updated title",
            "description": "Updated desc",
            "status": "In Progress",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Updated title" in resp.data
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            assert task.status == "In Progress"

    def test_edit_empty_title_returns_422(self, client, app, sample_task):
        resp = client.post(f"/tasks/{sample_task}/edit", data={
            "title": "",
            "status": "Pending",
        })
        assert resp.status_code == 422


# ── Integration tests: Delete ────────────────────────────────────────────────

class TestDelete:
    def test_delete_task(self, client, app, sample_task):
        resp = client.post(f"/tasks/{sample_task}/delete", follow_redirects=True)
        assert resp.status_code == 200
        assert b"deleted" in resp.data
        with app.app_context():
            assert _db.session.get(Task, sample_task) is None

    def test_delete_unknown_task_returns_404(self, client):
        resp = client.post("/tasks/99999/delete")
        assert resp.status_code == 404
