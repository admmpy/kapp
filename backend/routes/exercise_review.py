"""
Exercise review routes for sentence-level spaced repetition

Endpoints:
- GET /api/exercises/due - Get exercises due for review
- POST /api/exercises/:id/review - Record an SRS review for an exercise
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from database import db
from models_v2 import Exercise, ExerciseSRS
from srs_utils import apply_sm2
from utils import not_found_response, error_response, validation_error_response
from routes.helpers import get_current_user_id
import logging

logger = logging.getLogger(__name__)

exercise_review_bp = Blueprint("exercise_review", __name__)


@exercise_review_bp.route("/exercises/due", methods=["GET"])
def get_due_exercises():
    """
    Get exercises due for SRS review.

    Query params:
        - limit: Max items to return (default 20)

    Response:
        {
            "exercises": [...],
            "total_due": 15,
            "new_items": 5
        }
    """
    if not current_app.config.get("SENTENCE_SRS_ENABLED"):
        return jsonify({"exercises": [], "total_due": 0, "new_items": 0}), 200

    try:
        limit = min(request.args.get("limit", 20, type=int), 50)
        user_id = get_current_user_id()
        now = datetime.utcnow()

        # Get SRS records due for review
        due_srs = (
            db.session.query(ExerciseSRS)
            .filter(
                ExerciseSRS.user_id == user_id,
                db.or_(
                    ExerciseSRS.next_review_date.is_(None),
                    ExerciseSRS.next_review_date <= now,
                ),
            )
            .order_by(
                ExerciseSRS.next_review_date.asc().nulls_first(),
            )
            .limit(limit)
            .all()
        )

        new_count = sum(1 for srs in due_srs if srs.next_review_date is None)

        exercises = []
        for srs in due_srs:
            ex = srs.exercise
            if not ex:
                continue

            exercise_data = {
                "id": ex.id,
                "exercise_type": ex.exercise_type.value,
                "question": ex.question,
                "instruction": ex.instruction,
                "display_order": ex.display_order,
                # Review mode requires local answer reveal before final quality submit.
                "correct_answer": ex.correct_answer,
                "explanation": ex.explanation,
            }

            if ex.korean_text:
                exercise_data["korean_text"] = ex.korean_text
            if ex.romanization:
                exercise_data["romanization"] = ex.romanization
            if ex.english_text:
                exercise_data["english_text"] = ex.english_text
            if ex.content_text:
                exercise_data["content_text"] = ex.content_text
            if ex.audio_url:
                exercise_data["audio_url"] = ex.audio_url
            if ex.options:
                try:
                    exercise_data["options"] = json.loads(ex.options)
                except json.JSONDecodeError:
                    exercise_data["options"] = []

            # Add SRS metadata
            exercise_data["srs"] = {
                "exercise_id": ex.id,
                "next_review_date": srs.next_review_date.isoformat() if srs.next_review_date else None,
                "review_interval": srs.review_interval,
                "repetitions": srs.repetitions,
                "ease_factor": srs.ease_factor,
            }

            # Add lesson title for context
            if ex.lesson:
                exercise_data["lesson_title"] = ex.lesson.title

            exercises.append(exercise_data)

        return jsonify({
            "exercises": exercises,
            "total_due": len(exercises),
            "new_items": new_count,
        }), 200

    except Exception as e:
        logger.error(f"Error getting due exercises: {e}")
        return error_response("Failed to get due exercises", 500)


@exercise_review_bp.route("/exercises/<int:exercise_id>/review", methods=["POST"])
def record_exercise_review(exercise_id: int):
    """
    Record an SRS review for an exercise.

    Request body:
        {
            "quality": 4  // 0-5 rating
        }

    Response:
        {
            "success": true,
            "next_review_date": "2024-01-21T10:00:00",
            "review_interval": 6,
            "repetitions": 3,
            "ease_factor": 2.6
        }
    """
    if not current_app.config.get("SENTENCE_SRS_ENABLED"):
        return error_response("Sentence SRS is not enabled", 400)

    try:
        exercise = db.session.get(Exercise, exercise_id)
        if not exercise:
            return not_found_response("Exercise")

        data = request.get_json()
        if data is None or "quality" not in data:
            return validation_error_response("quality field is required")

        quality = int(data["quality"])
        if quality < 0 or quality > 5:
            return validation_error_response("quality must be between 0 and 5")

        user_id = get_current_user_id()

        # Get or create SRS record
        srs = (
            db.session.query(ExerciseSRS)
            .filter(
                ExerciseSRS.user_id == user_id,
                ExerciseSRS.exercise_id == exercise_id,
            )
            .first()
        )

        if not srs:
            srs = ExerciseSRS(
                user_id=user_id,
                exercise_id=exercise_id,
                times_practiced=0,
                times_correct=0,
                review_interval=1,
                ease_factor=2.5,
                repetitions=0,
            )
            db.session.add(srs)

        # Update practice stats
        srs.times_practiced += 1
        if quality >= 3:
            srs.times_correct += 1
        srs.last_reviewed_at = datetime.utcnow()

        # Apply SM-2 algorithm
        apply_sm2(srs, quality)

        db.session.commit()

        return jsonify({
            "success": True,
            "next_review_date": srs.next_review_date.isoformat() if srs.next_review_date else None,
            "review_interval": srs.review_interval,
            "repetitions": srs.repetitions,
            "ease_factor": srs.ease_factor,
        }), 200

    except ValueError:
        return validation_error_response("quality must be an integer")
    except Exception as e:
        logger.error(f"Error recording exercise review for {exercise_id}: {e}")
        db.session.rollback()
        return error_response("Failed to record exercise review", 500)
