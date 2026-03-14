"""
Task Routes
-----------
All CRUD endpoints for the Task resource, registered on a Blueprint
so they can be independently imported, tested, or versioned.
"""

from datetime import datetime, timezone
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from ..models import db, Task, TaskStatus

tasks_bp = Blueprint("tasks", __name__)


# ── Helpers ────────────────────────────────────────────────────────────────

def _validate_task_form(title: str, status: str) -> list[str]:
    """
    Validate common task form fields.

    Returns a list of human-readable error strings (empty = valid).
    Kept as a standalone function so unit tests can call it directly.
    """
    errors: list[str] = []

    if not title or not title.strip():
        errors.append("Title is required and cannot be blank.")
    elif len(title.strip()) > 200:
        errors.append("Title must be 200 characters or fewer.")

    if status not in TaskStatus.values():
        errors.append(f"Invalid status '{status}'.")

    return errors


# ── Routes ─────────────────────────────────────────────────────────────────

@tasks_bp.route("/")
def index():
    """Dashboard: list all tasks, with optional status filter."""
    status_filter = request.args.get("status", "").strip()
    valid_statuses = TaskStatus.values()

    query = db.select(Task).order_by(Task.created_at.desc())
    if status_filter and status_filter in valid_statuses:
        query = query.where(Task.status == status_filter)

    tasks = db.session.scalars(query).all()

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        statuses=valid_statuses,
        current_filter=status_filter,
    )


@tasks_bp.route("/tasks/new", methods=["GET", "POST"])
def create():
    """Create a new task."""
    statuses = TaskStatus.values()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", TaskStatus.PENDING.value)

        errors = _validate_task_form(title, status)

        if errors:
            for error in errors:
                flash(error, "error")
            # Re-render with the user's input preserved
            return render_template(
                "tasks/form.html",
                action="Create",
                statuses=statuses,
                form_data={"title": title, "description": description, "status": status},
            ), 422

        task = Task(title=title, description=description or None, status=status)
        db.session.add(task)
        db.session.commit()
        flash(f"Task '{task.title}' created successfully.", "success")
        return redirect(url_for("tasks.index"))

    return render_template(
        "tasks/form.html",
        action="Create",
        statuses=statuses,
        form_data={"title": "", "description": "", "status": TaskStatus.PENDING.value},
    )


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit(task_id: int):
    """Edit an existing task. Returns 404 if the task does not exist."""
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    statuses = TaskStatus.values()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", task.status)

        errors = _validate_task_form(title, status)

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "tasks/form.html",
                action="Update",
                task=task,
                statuses=statuses,
                form_data={"title": title, "description": description, "status": status},
            ), 422

        task.title = title
        task.description = description or None
        task.status = status
        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f"Task '{task.title}' updated successfully.", "success")
        return redirect(url_for("tasks.index"))

    return render_template(
        "tasks/form.html",
        action="Update",
        task=task,
        statuses=statuses,
        form_data={
            "title": task.title,
            "description": task.description or "",
            "status": task.status,
        },
    )


@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete(task_id: int):
    """Delete a task. Returns 404 if the task does not exist."""
    task = db.session.get(Task, task_id)
    if task is None:
        abort(404)

    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash(f"Task '{title}' deleted.", "success")
    return redirect(url_for("tasks.index"))


# ── Error handlers ─────────────────────────────────────────────────────────

@tasks_bp.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html"), 404


@tasks_bp.app_errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500
