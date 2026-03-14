"""
Task Tracker Application Factory
---------------------------------
Uses the Application Factory pattern for modularity and testability.
"""

from flask import Flask
from .models import db
from .routes import tasks_bp


def create_app(config: dict | None = None) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config: Optional dict of configuration overrides (useful for testing).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── Default configuration ──────────────────────────────────────────────
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI="sqlite:///tasks.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Allow test/production overrides
    if config:
        app.config.from_mapping(config)

    # ── Extensions ─────────────────────────────────────────────────────────
    db.init_app(app)

    # ── Blueprints ─────────────────────────────────────────────────────────
    app.register_blueprint(tasks_bp)

    # ── Database initialisation ────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
