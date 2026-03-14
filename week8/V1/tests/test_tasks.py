"""
Unit tests for the Task Tracker application.

Run with:  pytest tests/
"""
import pytest

from app import create_app
from app.extensions import db as _db
from app.models.task import Task, TaskStatus


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture()
def app():
    """Application instance backed by an in-memory SQLite database."""
    flask_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
        }
    )
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def sample_task(app):
    """A pre-inserted task available for edit/delete tests."""
    with app.app_context():
        task = Task(title="Sample Task", description="A test task", status=TaskStatus.PENDING.value)
        _db.session.add(task)
        _db.session.commit()
        return task.id  # return id so tests can re-query inside app context


# ── Model tests ────────────────────────────────────────────────────────────

class TestTaskModel:
    def test_all_statuses_returns_three_values(self, app):
        with app.app_context():
            statuses = Task.all_statuses()
        assert len(statuses) == 3
        assert "Pending" in statuses
        assert "In Progress" in statuses
        assert "Completed" in statuses

    def test_task_defaults_to_pending(self, app):
        with app.app_context():
            task = Task(title="Default status task")
            _db.session.add(task)
            _db.session.commit()
            assert task.status == TaskStatus.PENDING.value

    def test_task_repr(self, app):
        with app.app_context():
            task = Task(title="Repr test", status=TaskStatus.COMPLETED.value)
            assert "Repr test" in repr(task)


# ── Dashboard tests ────────────────────────────────────────────────────────

class TestDashboard:
    def test_dashboard_loads(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert b"TaskTrack" in r.data

    def test_dashboard_lists_tasks(self, client, app, sample_task):
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            title = task.title
        r = client.get("/")
        assert title.encode() in r.data

    def test_dashboard_status_filter(self, client, app, sample_task):
        r = client.get("/?status=Pending")
        assert r.status_code == 200

    def test_dashboard_invalid_filter_ignored(self, client):
        r = client.get("/?status=bogus")
        assert r.status_code == 200


# ── Create tests ───────────────────────────────────────────────────────────

class TestCreateTask:
    def test_get_new_form(self, client):
        r = client.get("/tasks/new")
        assert r.status_code == 200
        assert b"New Task" in r.data

    def test_create_valid_task(self, client, app):
        r = client.post("/tasks/new", data={"title": "Buy milk", "description": "", "status": "Pending"})
        assert r.status_code in (302, 200)
        with app.app_context():
            task = Task.query.filter_by(title="Buy milk").first()
            assert task is not None

    def test_create_empty_title_fails(self, client):
        r = client.post("/tasks/new", data={"title": "   ", "status": "Pending"})
        assert r.status_code == 422
        assert b"required" in r.data.lower() or b"Title" in r.data

    def test_create_missing_title_fails(self, client):
        r = client.post("/tasks/new", data={"title": "", "status": "Pending"})
        assert r.status_code == 422

    def test_create_invalid_status_fails(self, client):
        r = client.post("/tasks/new", data={"title": "Valid title", "status": "Nonexistent"})
        assert r.status_code == 422

    def test_flash_success_on_create(self, client):
        r = client.post(
            "/tasks/new",
            data={"title": "Flash test", "status": "Pending"},
            follow_redirects=True,
        )
        assert b"created successfully" in r.data


# ── Edit tests ─────────────────────────────────────────────────────────────

class TestEditTask:
    def test_get_edit_form(self, client, app, sample_task):
        r = client.get(f"/tasks/{sample_task}/edit")
        assert r.status_code == 200
        assert b"Edit Task" in r.data

    def test_edit_404_for_missing_id(self, client):
        r = client.get("/tasks/9999/edit")
        assert r.status_code == 404

    def test_update_task(self, client, app, sample_task):
        r = client.post(
            f"/tasks/{sample_task}/edit",
            data={"title": "Updated Title", "status": "In Progress"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            assert task.title == "Updated Title"
            assert task.status == "In Progress"

    def test_update_empty_title_fails(self, client, app, sample_task):
        r = client.post(
            f"/tasks/{sample_task}/edit",
            data={"title": "", "status": "Pending"},
        )
        assert r.status_code == 422

    def test_update_404_for_missing_id(self, client):
        r = client.post("/tasks/9999/edit", data={"title": "x", "status": "Pending"})
        assert r.status_code == 404


# ── Delete tests ───────────────────────────────────────────────────────────

class TestDeleteTask:
    def test_delete_task(self, client, app, sample_task):
        r = client.post(f"/tasks/{sample_task}/delete", follow_redirects=True)
        assert r.status_code == 200
        with app.app_context():
            task = _db.session.get(Task, sample_task)
            assert task is None

    def test_delete_404_for_missing_id(self, client):
        r = client.post("/tasks/9999/delete")
        assert r.status_code == 404

    def test_flash_on_delete(self, client, app, sample_task):
        r = client.post(f"/tasks/{sample_task}/delete", follow_redirects=True)
        assert b"deleted" in r.data
