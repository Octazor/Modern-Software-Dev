"""
Tasks blueprint — all CRUD routes for the Task resource.

Route map
---------
GET  /                  → dashboard (list all tasks)
GET  /tasks/new         → blank create form
POST /tasks/new         → handle create submission
GET  /tasks/<id>/edit   → pre-filled edit form
POST /tasks/<id>/edit   → handle update submission
POST /tasks/<id>/delete → handle delete (no JS needed — plain form POST)
"""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..extensions import db
from ..models.task import Task, TaskStatus

tasks_bp = Blueprint("tasks", __name__)

# ── Helpers ────────────────────────────────────────────────────────────────


def _validate_task_form(title: str, status: str) -> list[str]:
    """Return a list of human-readable validation error strings (empty = valid)."""
    errors: list[str] = []

    if not title or not title.strip():
        errors.append("Title is required and cannot be blank.")
    elif len(title.strip()) > 200:
        errors.append("Title must be 200 characters or fewer.")

    if status not in Task.all_statuses():
        errors.append(f"'{status}' is not a valid status.")

    return errors


# ── Routes ─────────────────────────────────────────────────────────────────


@tasks_bp.get("/")
def dashboard() -> str:
    """List all tasks, optionally filtered by status."""
    status_filter = request.args.get("status", "").strip()
    query = Task.query.order_by(Task.created_at.desc())

    if status_filter and status_filter in Task.all_statuses():
        query = query.filter_by(status=status_filter)
        active_filter = status_filter
    else:
        active_filter = ""

    tasks = query.all()
    counts = {s: Task.query.filter_by(status=s).count() for s in Task.all_statuses()}

    return render_template(
        "tasks/dashboard.html",
        tasks=tasks,
        statuses=Task.all_statuses(),
        active_filter=active_filter,
        counts=counts,
    )


@tasks_bp.get("/tasks/new")
def new_task() -> str:
    return render_template("tasks/form.html", task=None, statuses=Task.all_statuses())


@tasks_bp.post("/tasks/new")
def create_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", TaskStatus.PENDING.value)

    errors = _validate_task_form(title, status)
    if errors:
        for err in errors:
            flash(err, "error")
        return (
            render_template(
                "tasks/form.html",
                task=None,
                statuses=Task.all_statuses(),
                form_data={"title": title, "description": description, "status": status},
            ),
            422,
        )

    task = Task(title=title, description=description or None, status=status)
    db.session.add(task)
    db.session.commit()

    flash(f"Task '{task.title}' created successfully.", "success")
    return redirect(url_for("tasks.dashboard"))


@tasks_bp.get("/tasks/<int:task_id>/edit")
def edit_task(task_id: int) -> str:
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)
    return render_template("tasks/form.html", task=task, statuses=Task.all_statuses())


@tasks_bp.post("/tasks/<int:task_id>/edit")
def update_task(task_id: int):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", TaskStatus.PENDING.value)

    errors = _validate_task_form(title, status)
    if errors:
        for err in errors:
            flash(err, "error")
        return (
            render_template(
                "tasks/form.html",
                task=task,
                statuses=Task.all_statuses(),
                form_data={"title": title, "description": description, "status": status},
            ),
            422,
        )

    task.title = title
    task.description = description or None
    task.status = status
    db.session.commit()

    flash(f"Task '{task.title}' updated successfully.", "success")
    return redirect(url_for("tasks.dashboard"))


@tasks_bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int):
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    title = task.title
    db.session.delete(task)
    db.session.commit()

    flash(f"Task '{title}' deleted.", "success")
    return redirect(url_for("tasks.dashboard"))
