"""
Task model — represents a single project task.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from ..extensions import db


class TaskStatus(str, enum.Enum):
    """Allowed status values for a Task.

    Inheriting from *str* lets Jinja2 compare values directly with string
    literals (e.g. ``task.status == 'pending'``) and ensures SQLAlchemy
    stores a human-readable string rather than an integer ordinal.
    """

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class Task(db.Model):
    """Persistent task entity."""

    __tablename__ = "tasks"

    id: db.Mapped[int] = db.mapped_column(primary_key=True)
    title: db.Mapped[str] = db.mapped_column(db.String(200), nullable=False)
    description: db.Mapped[str | None] = db.mapped_column(db.Text, nullable=True)
    status: db.Mapped[str] = db.mapped_column(
        db.String(20),
        nullable=False,
        default=TaskStatus.PENDING.value,
    )
    created_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Helpers ────────────────────────────────────────────────────────────

    @classmethod
    def all_statuses(cls) -> list[str]:
        """Return every valid status value — used to populate <select> menus."""
        return [s.value for s in TaskStatus]

    def __repr__(self) -> str:
        return f"<Task id={self.id!r} title={self.title!r} status={self.status!r}>"
