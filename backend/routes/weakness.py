"""
Weakness review routes for weakness-driven practice

Endpoints:
- GET /api/review/weaknesses - Get weakest grammar patterns and vocabulary
- GET /api/review/weakness-exercises - Get exercises targeting weak areas
"""
import json
from flask import Blueprint, request, jsonify, current_app
from database import db
from models_v2 import GrammarMastery, GrammarPattern, Exercise, VocabularyItem
from utils import error_response
from routes.helpers import get_current_user_id
import logging

logger = logging.getLogger(__name__)

weakness_bp = Blueprint("weakness", __name__)


@weakness_bp.route("/review/weaknesses", methods=["GET"])
def get_weaknesses():
    """
    Get weakest grammar patterns and vocabulary items.

    Response:
        {
            "weak_grammar": [...],
            "weak_vocabulary": [...]
        }
    """
    if not current_app.config.get("WEAKNESS_REVIEW_ENABLED"):
        return jsonify({"weak_grammar": [], "weak_vocabulary": []}), 200

    try:
        user_id = get_current_user_id()
        limit = min(request.args.get("limit", 10, type=int), 20)

        # Get weak grammar patterns (mastery < 80%, at least 1 attempt)
        weak_grammar_records = (
            db.session.query(GrammarMastery, GrammarPattern)
            .join(GrammarPattern, GrammarMastery.pattern_id == GrammarPattern.id)
            .filter(
                GrammarMastery.user_id == user_id,
                GrammarMastery.attempts > 0,
                GrammarMastery.mastery_score < 80,
            )
            .order_by(GrammarMastery.mastery_score.asc())
            .limit(limit)
            .all()
        )

        weak_grammar = []
        for mastery, pattern in weak_grammar_records:
            # Get exercise IDs linked to this pattern
            exercise_ids = [
                ex.id for ex in
                db.session.query(Exercise.id)
                .filter(Exercise.grammar_pattern_id == pattern.id)
                .all()
            ]
            weak_grammar.append({
                "pattern_id": pattern.id,
                "pattern_title": pattern.title,
                "mastery_score": mastery.mastery_score,
                "attempts": mastery.attempts,
                "correct": mastery.correct,
                "exercise_ids": exercise_ids,
            })

        # Get weak vocabulary (accuracy < 80%, at least 1 practice)
        weak_vocab_items = (
            db.session.query(VocabularyItem)
            .filter(
                VocabularyItem.times_practiced > 0,
            )
            .all()
        )

        # Filter by computed accuracy rate and sort
        weak_vocabulary = []
        for item in weak_vocab_items:
            accuracy = item.accuracy_rate
            if accuracy is not None and accuracy < 80:
                weak_vocabulary.append({
                    "id": item.id,
                    "korean": item.korean,
                    "english": item.english,
                    "romanization": item.romanization,
                    "accuracy_rate": round(accuracy, 1),
                    "times_practiced": item.times_practiced,
                })

        weak_vocabulary.sort(key=lambda x: x["accuracy_rate"])
        weak_vocabulary = weak_vocabulary[:limit]

        return jsonify({
            "weak_grammar": weak_grammar,
            "weak_vocabulary": weak_vocabulary,
        }), 200

    except Exception as e:
        logger.error(f"Error getting weaknesses: {e}")
        return error_response("Failed to get weaknesses", 500)


@weakness_bp.route("/review/weakness-exercises", methods=["GET"])
def get_weakness_exercises():
    """
    Get exercises targeting the weakest grammar patterns.

    Query params:
        - limit: Max exercises to return (default 20)

    Response:
        {
            "exercises": [...]
        }
    """
    if not current_app.config.get("WEAKNESS_REVIEW_ENABLED"):
        return jsonify({"exercises": []}), 200

    try:
        user_id = get_current_user_id()
        limit = min(request.args.get("limit", 20, type=int), 50)

        # Get weakest grammar patterns
        weak_pattern_ids = (
            db.session.query(GrammarMastery.pattern_id)
            .filter(
                GrammarMastery.user_id == user_id,
                GrammarMastery.attempts > 0,
                GrammarMastery.mastery_score < 80,
            )
            .order_by(GrammarMastery.mastery_score.asc())
            .limit(10)
            .all()
        )
        pattern_ids = [pid for (pid,) in weak_pattern_ids]

        exercises = []
        if pattern_ids:
            weak_exercises = (
                db.session.query(Exercise)
                .filter(Exercise.grammar_pattern_id.in_(pattern_ids))
                .limit(limit)
                .all()
            )

            for ex in weak_exercises:
                exercise_data = {
                    "id": ex.id,
                    "exercise_type": ex.exercise_type.value,
                    "question": ex.question,
                    "instruction": ex.instruction,
                    "display_order": ex.display_order,
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

                if ex.lesson:
                    exercise_data["lesson_title"] = ex.lesson.title

                exercises.append(exercise_data)

        return jsonify({"exercises": exercises}), 200

    except Exception as e:
        logger.error(f"Error getting weakness exercises: {e}")
        return error_response("Failed to get weakness exercises", 500)
