"""SQLAlchemy database setup

This module configures Flask-SQLAlchemy and provides database connection management.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


# Initialize SQLAlchemy with custom base
db = SQLAlchemy(model_class=Base)


def init_db(app):
    """Initialize database with Flask app

    Args:
        app: Flask application instance
    """
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully")


def get_db():
    """Get database instance for use in other modules

    Returns:
        SQLAlchemy database instance
    """
    return db
