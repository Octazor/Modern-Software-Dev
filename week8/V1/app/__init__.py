"""
Task Tracker — Flask Application Factory
"""
from flask import Flask
from .extensions import db


def create_app(config: dict | None = None) -> Flask:
    """
    Application factory.  Accepts an optional config dict so that tests
    can pass in test-specific settings (e.g. an in-memory SQLite database)
    without touching the real configuration file.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── Default configuration ──────────────────────────────────────────────
    app.config.from_mapping(
        SECRET_KEY="change-me-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///tasks.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Overlay caller-supplied overrides (useful for tests)
    if config:
        app.config.from_mapping(config)

    # ── Extensions ─────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Blueprints ─────────────────────────────────────────────────────────
    from .routes.tasks import tasks_bp  # noqa: PLC0415

    app.register_blueprint(tasks_bp)

    # ── Database bootstrap ─────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
