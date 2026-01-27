"""
Course routes for retrieving courses, units, and lessons structure

Endpoints:
- GET /api/courses - List all courses
- GET /api/courses/:id - Get course with units
- GET /api/units/:id - Get unit details
- GET /api/units/:id/lessons - Get lessons in unit
"""
from flask import Blueprint, jsonify
from database import db
from models_v2 import Course, Unit, Lesson, UserProgress
from utils import not_found_response, error_response
import logging

logger = logging.getLogger(__name__)

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/courses", methods=["GET"])
def list_courses():
    """
    List all active courses

    Response:
        {
            "courses": [
                {
                    "id": 1,
                    "title": "Korean Fundamentals",
                    "description": "...",
                    "level": "Beginner",
                    "unit_count": 5,
                    "total_lessons": 32,
                    "image_url": "..."
                },
                ...
            ]
        }
    """
    try:
        courses = (
            db.session.query(Course)
            .filter(Course.is_active == True)  # noqa: E712
            .order_by(Course.display_order)
            .all()
        )

        result = []
        for course in courses:
            result.append(
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "language": course.language,
                    "level": course.level,
                    "unit_count": course.unit_count,
                    "total_lessons": course.total_lessons,
                    "image_url": course.image_url,
                }
            )

        return jsonify({"courses": result}), 200

    except Exception as e:
        logger.error(f"Error listing courses: {e}")
        return error_response("Failed to list courses", 500, str(e))


@courses_bp.route("/courses/<int:course_id>", methods=["GET"])
def get_course(course_id: int):
    """
    Get course details with units

    Response:
        {
            "course": {
                "id": 1,
                "title": "Korean Fundamentals",
                "description": "...",
                "level": "Beginner",
                "units": [
                    {
                        "id": 1,
                        "title": "Unit 1: Greetings",
                        "description": "...",
                        "lesson_count": 8,
                        "is_locked": false
                    },
                    ...
                ]
            }
        }
    """
    try:
        course = db.session.get(Course, course_id)
        if not course:
            return not_found_response("Course")

        units = []
        for unit in course.units:
            units.append(
                {
                    "id": unit.id,
                    "title": unit.title,
                    "description": unit.description,
                    "lesson_count": unit.lesson_count,
                    "display_order": unit.display_order,
                    "is_locked": unit.is_locked,
                }
            )

        return (
            jsonify(
                {
                    "course": {
                        "id": course.id,
                        "title": course.title,
                        "description": course.description,
                        "language": course.language,
                        "level": course.level,
                        "image_url": course.image_url,
                        "units": units,
                    }
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting course {course_id}: {e}")
        return error_response("Failed to get course", 500, str(e))


@courses_bp.route("/units/<int:unit_id>", methods=["GET"])
def get_unit(unit_id: int):
    """
    Get unit details

    Response:
        {
            "unit": {
                "id": 1,
                "title": "Unit 1: Greetings",
                "description": "...",
                "course_id": 1,
                "lesson_count": 8,
                "is_locked": false
            }
        }
    """
    try:
        unit = db.session.get(Unit, unit_id)
        if not unit:
            return not_found_response("Unit")

        return (
            jsonify(
                {
                    "unit": {
                        "id": unit.id,
                        "title": unit.title,
                        "description": unit.description,
                        "course_id": unit.course_id,
                        "lesson_count": unit.lesson_count,
                        "display_order": unit.display_order,
                        "is_locked": unit.is_locked,
                    }
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting unit {unit_id}: {e}")
        return error_response("Failed to get unit", 500, str(e))


@courses_bp.route("/units/<int:unit_id>/lessons", methods=["GET"])
def get_unit_lessons(unit_id: int):
    """
    Get lessons in a unit with progress info

    Response:
        {
            "unit": {
                "id": 1,
                "title": "Unit 1: Greetings"
            },
            "lessons": [
                {
                    "id": 1,
                    "title": "Hello & Goodbye",
                    "description": "...",
                    "estimated_minutes": 5,
                    "exercise_count": 8,
                    "is_locked": false,
                    "is_completed": false,
                    "score": null
                },
                ...
            ]
        }
    """
    try:
        unit = db.session.get(Unit, unit_id)
        if not unit:
            return not_found_response("Unit")

        # Get user progress for all lessons in this unit (user_id=1 for now)
        progress_map = {}
        progress_records = (
            db.session.query(UserProgress)
            .filter(
                UserProgress.lesson_id.in_([l.id for l in unit.lessons]),
                UserProgress.user_id == 1,
            )
            .all()
        )
        for p in progress_records:
            progress_map[p.lesson_id] = p

        lessons = []
        for lesson in unit.lessons:
            progress = progress_map.get(lesson.id)
            lessons.append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "estimated_minutes": lesson.estimated_minutes,
                    "exercise_count": lesson.exercise_count,
                    "display_order": lesson.display_order,
                    "is_locked": lesson.is_locked,
                    "is_started": progress.is_started if progress else False,
                    "is_completed": progress.is_completed if progress else False,
                    "score": progress.score if progress else None,
                }
            )

        return (
            jsonify({"unit": {"id": unit.id, "title": unit.title}, "lessons": lessons}),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting lessons for unit {unit_id}: {e}")
        return error_response("Failed to get lessons", 500, str(e))
