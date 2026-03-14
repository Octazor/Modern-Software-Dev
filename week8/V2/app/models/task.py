"""
Task Model
----------
Defines the Task database model and its related enum.
"""

import enum
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TaskStatus(enum.Enum):
    """Allowed statuses for a Task."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

    @classmethod
    def values(cls) -> list[str]:
        """Return a list of string values for use in templates / validation."""
        return [member.value for member in cls]


class Task(db.Model):
    """
    Represents a single project task.

    Attributes:
        id          -- Auto-incrementing primary key.
        title       -- Short, required summary of the task.
        description -- Optional long-form detail.
        status      -- Current lifecycle state (Pending / In Progress / Completed).
        created_at  -- UTC timestamp set on insert.
        updated_at  -- UTC timestamp updated on every save.
    """

    __tablename__ = "tasks"

    id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
    title: db.Mapped[str] = db.mapped_column(db.String(200), nullable=False)
    description: db.Mapped[str | None] = db.mapped_column(db.Text, nullable=True)
    status: db.Mapped[str] = db.mapped_column(
        db.String(20),
        nullable=False,
        default=TaskStatus.PENDING.value,
    )
    created_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status!r}>"

    def to_dict(self) -> dict:
        """Serialise the task – convenient for future API / test use."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
