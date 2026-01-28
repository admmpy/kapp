"""
Helper functions for route handlers

Consolidates common patterns used across route files.
"""
from database import db
from models_v2 import UserProgress


def get_current_user_id() -> int:
    """Get current user ID (placeholder for future auth)."""
    return 1


def get_user_progress(lesson_id: int, user_id: int = None) -> UserProgress | None:
    """Get user progress for a lesson.

    Args:
        lesson_id: The lesson ID to get progress for
        user_id: Optional user ID (defaults to current user)

    Returns:
        UserProgress object or None if not found
    """
    if user_id is None:
        user_id = get_current_user_id()

    return (
        db.session.query(UserProgress)
        .filter(UserProgress.lesson_id == lesson_id, UserProgress.user_id == user_id)
        .first()
    )


def get_or_create_user_progress(lesson_id: int, total_exercises: int = 0, user_id: int = None) -> UserProgress:
    """Get existing user progress or create a new one.

    Args:
        lesson_id: The lesson ID
        total_exercises: Number of exercises in the lesson (for new progress)
        user_id: Optional user ID (defaults to current user)

    Returns:
        UserProgress object (existing or newly created)
    """
    if user_id is None:
        user_id = get_current_user_id()

    progress = get_user_progress(lesson_id, user_id)

    if not progress:
        progress = UserProgress(
            lesson_id=lesson_id,
            user_id=user_id,
            total_exercises=total_exercises
        )
        db.session.add(progress)

    return progress
