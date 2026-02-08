"""
Vocabulary routes for vocabulary reference/glossary

Endpoints:
- GET /api/vocabulary - List vocabulary items
- GET /api/vocabulary/:id - Get vocabulary item details
- GET /api/vocabulary/categories - List categories
- POST /api/vocabulary/:id/practice - Record practice attempt
- GET /api/vocabulary/due - Get vocabulary items due for review (spaced repetition)
- POST /api/vocabulary/:id/review - Record a spaced repetition review
"""
from flask import Blueprint, request, jsonify
from database import db
from models_v2 import VocabularyItem
from utils import not_found_response, error_response, validation_error_response
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

vocabulary_bp = Blueprint("vocabulary", __name__)


@vocabulary_bp.route("/vocabulary", methods=["GET"])
def list_vocabulary():
    """
    List vocabulary items with filtering

    Query params:
        - category: Filter by category (e.g., "greetings")
        - difficulty: Filter by difficulty level (1-5)
        - search: Search in Korean or English
        - limit: Max items to return (default 50)
        - offset: Pagination offset

    Response:
        {
            "vocabulary": [
                {
                    "id": 1,
                    "korean": "안녕하세요",
                    "romanization": "annyeonghaseyo",
                    "english": "hello",
                    "part_of_speech": "phrase",
                    "category": "greetings",
                    "difficulty_level": 1,
                    "audio_url": "...",
                    "accuracy_rate": 85.0
                },
                ...
            ],
            "total": 150,
            "limit": 50,
            "offset": 0
        }
    """
    try:
        # Parse query parameters
        category = request.args.get("category")
        difficulty = request.args.get("difficulty", type=int)
        search = request.args.get("search", "").strip()
        limit = min(request.args.get("limit", 50, type=int), 100)
        offset = request.args.get("offset", 0, type=int)

        # Build query
        query = db.session.query(VocabularyItem)

        if category:
            query = query.filter(VocabularyItem.category == category)
        if difficulty:
            query = query.filter(VocabularyItem.difficulty_level == difficulty)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    VocabularyItem.korean.ilike(search_pattern),
                    VocabularyItem.english.ilike(search_pattern),
                    VocabularyItem.romanization.ilike(search_pattern),
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        items = (
            query.order_by(
                VocabularyItem.difficulty_level,
                VocabularyItem.category,
                VocabularyItem.korean,
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        vocabulary = []
        for item in items:
            vocabulary.append(
                {
                    "id": item.id,
                    "korean": item.korean,
                    "romanization": item.romanization,
                    "english": item.english,
                    "part_of_speech": item.part_of_speech,
                    "category": item.category,
                    "difficulty_level": item.difficulty_level,
                    "audio_url": item.audio_url,
                    "accuracy_rate": item.accuracy_rate,
                }
            )

        return (
            jsonify(
                {
                    "vocabulary": vocabulary,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error listing vocabulary: {e}")
        return error_response("Failed to list vocabulary", 500, str(e))


@vocabulary_bp.route("/vocabulary/<int:item_id>", methods=["GET"])
def get_vocabulary_item(item_id: int):
    """
    Get vocabulary item details

    Response:
        {
            "item": {
                "id": 1,
                "korean": "안녕하세요",
                "romanization": "annyeonghaseyo",
                "english": "hello",
                "part_of_speech": "phrase",
                "example_sentence_korean": "안녕하세요, 저는 민수입니다.",
                "example_sentence_english": "Hello, I am Minsu.",
                "category": "greetings",
                "difficulty_level": 1,
                "audio_url": "...",
                "times_practiced": 10,
                "times_correct": 8,
                "accuracy_rate": 80.0
            }
        }
    """
    try:
        item = db.session.get(VocabularyItem, item_id)
        if not item:
            return not_found_response("Vocabulary item")

        return (
            jsonify(
                {
                    "item": {
                        "id": item.id,
                        "korean": item.korean,
                        "romanization": item.romanization,
                        "english": item.english,
                        "part_of_speech": item.part_of_speech,
                        "example_sentence_korean": item.example_sentence_korean,
                        "example_sentence_english": item.example_sentence_english,
                        "category": item.category,
                        "difficulty_level": item.difficulty_level,
                        "audio_url": item.audio_url,
                        "times_practiced": item.times_practiced,
                        "times_correct": item.times_correct,
                        "accuracy_rate": item.accuracy_rate,
                    }
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting vocabulary item {item_id}: {e}")
        return error_response("Failed to get vocabulary item", 500, str(e))


@vocabulary_bp.route("/vocabulary/categories", methods=["GET"])
def list_categories():
    """
    List all vocabulary categories

    Response:
        {
            "categories": [
                {
                    "name": "greetings",
                    "count": 15
                },
                {
                    "name": "numbers",
                    "count": 20
                },
                ...
            ]
        }
    """
    try:
        # Get distinct categories with counts
        from sqlalchemy import func

        results = (
            db.session.query(
                VocabularyItem.category, func.count(VocabularyItem.id).label("count")
            )
            .filter(VocabularyItem.category.isnot(None))
            .group_by(VocabularyItem.category)
            .order_by(VocabularyItem.category)
            .all()
        )

        categories = [{"name": cat, "count": count} for cat, count in results]

        return jsonify({"categories": categories}), 200

    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        return error_response("Failed to list categories", 500, str(e))


@vocabulary_bp.route("/vocabulary/<int:item_id>/practice", methods=["POST"])
def record_practice(item_id: int):
    """
    Record a practice attempt for a vocabulary item

    Request body:
        {
            "correct": true
        }

    Response:
        {
            "success": true,
            "times_practiced": 11,
            "times_correct": 9,
            "accuracy_rate": 81.8
        }
    """
    try:
        item = db.session.get(VocabularyItem, item_id)
        if not item:
            return not_found_response("Vocabulary item")

        data = request.get_json()
        if data is None or "correct" not in data:
            return validation_error_response("correct field is required")

        is_correct = bool(data["correct"])

        item.times_practiced += 1
        if is_correct:
            item.times_correct += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "times_practiced": item.times_practiced,
                    "times_correct": item.times_correct,
                    "accuracy_rate": item.accuracy_rate,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error recording practice for item {item_id}: {e}")
        db.session.rollback()
        return error_response("Failed to record practice", 500, str(e))


def calculate_sm2_next_review(item: VocabularyItem, quality: int) -> None:
    """
    Calculate next review date using SM-2 algorithm.
    Delegates to shared srs_utils.apply_sm2.
    """
    from srs_utils import apply_sm2
    apply_sm2(item, quality)


@vocabulary_bp.route("/vocabulary/due", methods=["GET"])
def get_due_vocabulary():
    """
    Get vocabulary items due for review based on spaced repetition

    Query params:
        - limit: Max items to return (default 20)

    Response:
        {
            "vocabulary": [
                {
                    "id": 1,
                    "korean": "안녕하세요",
                    "english": "hello",
                    "next_review_date": "2024-01-15T10:00:00",
                    "review_interval": 6,
                    "repetitions": 2,
                    ...
                }
            ],
            "total_due": 15,
            "new_items": 5
        }
    """
    try:
        limit = min(request.args.get("limit", 20, type=int), 50)
        now = datetime.utcnow()

        # Get items due for review (next_review_date is null or past)
        due_items = (
            db.session.query(VocabularyItem)
            .filter(
                db.or_(
                    VocabularyItem.next_review_date.is_(None),
                    VocabularyItem.next_review_date <= now
                )
            )
            .order_by(
                VocabularyItem.next_review_date.asc().nulls_first(),
                VocabularyItem.difficulty_level.asc()
            )
            .limit(limit)
            .all()
        )

        # Count new items (never reviewed)
        new_count = sum(1 for item in due_items if item.next_review_date is None)

        vocabulary = []
        for item in due_items:
            vocabulary.append({
                "id": item.id,
                "korean": item.korean,
                "romanization": item.romanization,
                "english": item.english,
                "part_of_speech": item.part_of_speech,
                "category": item.category,
                "difficulty_level": item.difficulty_level,
                "audio_url": item.audio_url,
                "next_review_date": item.next_review_date.isoformat() if item.next_review_date else None,
                "review_interval": item.review_interval,
                "repetitions": item.repetitions,
                "ease_factor": item.ease_factor,
            })

        return jsonify({
            "vocabulary": vocabulary,
            "total_due": len(due_items),
            "new_items": new_count,
        }), 200

    except Exception as e:
        logger.error(f"Error getting due vocabulary: {e}")
        return error_response("Failed to get due vocabulary", 500, str(e))


@vocabulary_bp.route("/vocabulary/<int:item_id>/review", methods=["POST"])
def record_review(item_id: int):
    """
    Record a spaced repetition review for a vocabulary item

    Request body:
        {
            "quality": 4  // 0-5 rating (0=complete blackout, 5=perfect recall)
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
    try:
        item = db.session.get(VocabularyItem, item_id)
        if not item:
            return not_found_response("Vocabulary item")

        data = request.get_json()
        if data is None or "quality" not in data:
            return validation_error_response("quality field is required")

        quality = int(data["quality"])
        if quality < 0 or quality > 5:
            return validation_error_response("quality must be between 0 and 5")

        # Update practice statistics
        item.times_practiced += 1
        if quality >= 3:
            item.times_correct += 1

        # Calculate next review using SM-2
        calculate_sm2_next_review(item, quality)

        db.session.commit()

        return jsonify({
            "success": True,
            "next_review_date": item.next_review_date.isoformat() if item.next_review_date else None,
            "review_interval": item.review_interval,
            "repetitions": item.repetitions,
            "ease_factor": item.ease_factor,
        }), 200

    except ValueError:
        return validation_error_response("quality must be an integer")
    except Exception as e:
        logger.error(f"Error recording review for item {item_id}: {e}")
        db.session.rollback()
        return error_response("Failed to record review", 500, str(e))
