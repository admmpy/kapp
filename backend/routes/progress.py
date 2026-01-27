"""
Progress routes for user progress tracking

Endpoints:
- GET /api/progress - Overall progress
- GET /api/progress/recent - Recent activity
- GET /api/progress/stats - Learning statistics
"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from sqlalchemy import func
from database import db
from models_v2 import Course, Unit, Lesson, UserProgress
from utils import error_response
import logging

logger = logging.getLogger(__name__)

progress_bp = Blueprint("progress", __name__)


@progress_bp.route("/progress", methods=["GET"])
def get_overall_progress():
    """
    Get overall learning progress

    Response:
        {
            "progress": {
                "total_lessons": 32,
                "completed_lessons": 8,
                "completion_percentage": 25.0,
                "total_time_spent_minutes": 120,
                "average_score": 85.5,
                "current_streak": 3,
                "courses": [
                    {
                        "id": 1,
                        "title": "Korean Fundamentals",
                        "completed_lessons": 8,
                        "total_lessons": 32,
                        "percentage": 25.0
                    }
                ]
            }
        }
    """
    try:
        user_id = 1  # Default user for now

        # Get all courses with their progress
        courses = (
            db.session.query(Course).filter(Course.is_active == True).all()
        )  # noqa: E712

        course_progress = []
        total_lessons = 0
        total_completed = 0
        total_time_seconds = 0
        scores = []

        for course in courses:
            course_lesson_ids = []
            for unit in course.units:
                for lesson in unit.lessons:
                    course_lesson_ids.append(lesson.id)

            course_total = len(course_lesson_ids)
            total_lessons += course_total

            if course_lesson_ids:
                # Get completed lessons for this course
                completed = (
                    db.session.query(UserProgress)
                    .filter(
                        UserProgress.lesson_id.in_(course_lesson_ids),
                        UserProgress.user_id == user_id,
                        UserProgress.is_completed == True,  # noqa: E712
                    )
                    .all()
                )

                course_completed = len(completed)
                total_completed += course_completed

                for p in completed:
                    total_time_seconds += p.time_spent_seconds or 0
                    if p.score is not None:
                        scores.append(p.score)

                course_progress.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "completed_lessons": course_completed,
                        "total_lessons": course_total,
                        "percentage": round((course_completed / course_total) * 100, 1)
                        if course_total > 0
                        else 0,
                    }
                )

        completion_percentage = (
            round((total_completed / total_lessons) * 100, 1)
            if total_lessons > 0
            else 0
        )
        average_score = round(sum(scores) / len(scores), 1) if scores else None

        # Calculate streak (days with activity in a row)
        streak = calculate_streak(user_id)

        return (
            jsonify(
                {
                    "progress": {
                        "total_lessons": total_lessons,
                        "completed_lessons": total_completed,
                        "completion_percentage": completion_percentage,
                        "total_time_spent_minutes": round(total_time_seconds / 60),
                        "average_score": average_score,
                        "current_streak": streak,
                        "courses": course_progress,
                    }
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting overall progress: {e}")
        return error_response("Failed to get progress", 500, str(e))


def calculate_streak(user_id: int) -> int:
    """Calculate current learning streak (consecutive days with completed lessons)"""
    try:
        today = datetime.utcnow().date()
        streak = 0

        # Check each day going backwards
        for days_ago in range(365):  # Max 1 year streak
            check_date = today - timedelta(days=days_ago)
            start_of_day = datetime.combine(check_date, datetime.min.time())
            end_of_day = datetime.combine(check_date, datetime.max.time())

            had_activity = (
                db.session.query(UserProgress)
                .filter(
                    UserProgress.user_id == user_id,
                    UserProgress.completed_at >= start_of_day,
                    UserProgress.completed_at <= end_of_day,
                )
                .first()
            )

            if had_activity:
                streak += 1
            elif days_ago > 0:  # Allow missing today
                break

        return streak

    except Exception:
        return 0


@progress_bp.route("/progress/recent", methods=["GET"])
def get_recent_activity():
    """
    Get recent learning activity

    Response:
        {
            "recent_activity": [
                {
                    "lesson_id": 5,
                    "lesson_title": "Numbers 1-10",
                    "unit_title": "Numbers & Counting",
                    "completed_at": "2024-01-15T10:35:00Z",
                    "score": 90.0
                },
                ...
            ]
        }
    """
    try:
        user_id = 1

        # Get recent completed lessons
        recent = (
            db.session.query(UserProgress)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.is_completed == True,  # noqa: E712
            )
            .order_by(UserProgress.completed_at.desc())
            .limit(10)
            .all()
        )

        activities = []
        for p in recent:
            lesson = db.session.get(Lesson, p.lesson_id)
            if lesson:
                unit = db.session.get(Unit, lesson.unit_id)
                activities.append(
                    {
                        "lesson_id": p.lesson_id,
                        "lesson_title": lesson.title,
                        "unit_title": unit.title if unit else None,
                        "completed_at": p.completed_at.isoformat()
                        if p.completed_at
                        else None,
                        "score": p.score,
                        "time_spent_minutes": round((p.time_spent_seconds or 0) / 60),
                    }
                )

        return jsonify({"recent_activity": activities}), 200

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return error_response("Failed to get recent activity", 500, str(e))


@progress_bp.route("/progress/stats", methods=["GET"])
def get_learning_stats():
    """
    Get detailed learning statistics

    Response:
        {
            "stats": {
                "lessons_completed_today": 2,
                "lessons_completed_this_week": 8,
                "total_exercises_completed": 150,
                "best_score": 100.0,
                "improvement_trend": 5.2,
                "most_practiced_category": "Greetings"
            }
        }
    """
    try:
        user_id = 1
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)

        # Lessons completed today
        start_of_today = datetime.combine(today, datetime.min.time())
        today_count = (
            db.session.query(func.count(UserProgress.id))
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.is_completed == True,  # noqa: E712
                UserProgress.completed_at >= start_of_today,
            )
            .scalar()
            or 0
        )

        # Lessons completed this week
        start_of_week = datetime.combine(week_ago, datetime.min.time())
        week_count = (
            db.session.query(func.count(UserProgress.id))
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.is_completed == True,  # noqa: E712
                UserProgress.completed_at >= start_of_week,
            )
            .scalar()
            or 0
        )

        # Total exercises completed
        total_exercises = (
            db.session.query(func.sum(UserProgress.completed_exercises))
            .filter(UserProgress.user_id == user_id)
            .scalar()
            or 0
        )

        # Best score
        best_score = (
            db.session.query(func.max(UserProgress.score))
            .filter(UserProgress.user_id == user_id, UserProgress.score.isnot(None))
            .scalar()
        )

        # Calculate improvement trend (compare last week's avg to previous week)
        improvement_trend = None
        # This would require more historical data, leaving as placeholder

        return (
            jsonify(
                {
                    "stats": {
                        "lessons_completed_today": today_count,
                        "lessons_completed_this_week": week_count,
                        "total_exercises_completed": total_exercises,
                        "best_score": best_score,
                        "improvement_trend": improvement_trend,
                        "current_streak": calculate_streak(user_id),
                    }
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting learning stats: {e}")
        return error_response("Failed to get stats", 500, str(e))
