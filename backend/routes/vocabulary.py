"""
Vocabulary routes for vocabulary reference/glossary

Endpoints:
- GET /api/vocabulary - List vocabulary items
- GET /api/vocabulary/:id - Get vocabulary item details
- GET /api/vocabulary/categories - List categories
- POST /api/vocabulary/:id/practice - Record practice attempt
"""
from flask import Blueprint, request, jsonify
from database import db
from models_v2 import VocabularyItem
from utils import not_found_response, error_response, validation_error_response
import logging

logger = logging.getLogger(__name__)

vocabulary_bp = Blueprint('vocabulary', __name__)


@vocabulary_bp.route('/vocabulary', methods=['GET'])
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
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        search = request.args.get('search', '').strip()
        limit = min(request.args.get('limit', 50, type=int), 100)
        offset = request.args.get('offset', 0, type=int)

        # Build query
        query = db.session.query(VocabularyItem)

        if category:
            query = query.filter(VocabularyItem.category == category)
        if difficulty:
            query = query.filter(VocabularyItem.difficulty_level == difficulty)
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    VocabularyItem.korean.ilike(search_pattern),
                    VocabularyItem.english.ilike(search_pattern),
                    VocabularyItem.romanization.ilike(search_pattern)
                )
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination and ordering
        items = query.order_by(
            VocabularyItem.difficulty_level,
            VocabularyItem.category,
            VocabularyItem.korean
        ).offset(offset).limit(limit).all()

        vocabulary = []
        for item in items:
            vocabulary.append({
                'id': item.id,
                'korean': item.korean,
                'romanization': item.romanization,
                'english': item.english,
                'part_of_speech': item.part_of_speech,
                'category': item.category,
                'difficulty_level': item.difficulty_level,
                'audio_url': item.audio_url,
                'accuracy_rate': item.accuracy_rate
            })

        return jsonify({
            'vocabulary': vocabulary,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Error listing vocabulary: {e}")
        return error_response('Failed to list vocabulary', 500, str(e))


@vocabulary_bp.route('/vocabulary/<int:item_id>', methods=['GET'])
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
            return not_found_response('Vocabulary item')

        return jsonify({
            'item': {
                'id': item.id,
                'korean': item.korean,
                'romanization': item.romanization,
                'english': item.english,
                'part_of_speech': item.part_of_speech,
                'example_sentence_korean': item.example_sentence_korean,
                'example_sentence_english': item.example_sentence_english,
                'category': item.category,
                'difficulty_level': item.difficulty_level,
                'audio_url': item.audio_url,
                'times_practiced': item.times_practiced,
                'times_correct': item.times_correct,
                'accuracy_rate': item.accuracy_rate
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting vocabulary item {item_id}: {e}")
        return error_response('Failed to get vocabulary item', 500, str(e))


@vocabulary_bp.route('/vocabulary/categories', methods=['GET'])
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

        results = db.session.query(
            VocabularyItem.category,
            func.count(VocabularyItem.id).label('count')
        ).filter(
            VocabularyItem.category.isnot(None)
        ).group_by(
            VocabularyItem.category
        ).order_by(
            VocabularyItem.category
        ).all()

        categories = [
            {'name': cat, 'count': count}
            for cat, count in results
        ]

        return jsonify({
            'categories': categories
        }), 200

    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        return error_response('Failed to list categories', 500, str(e))


@vocabulary_bp.route('/vocabulary/<int:item_id>/practice', methods=['POST'])
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
            return not_found_response('Vocabulary item')

        data = request.get_json()
        if data is None or 'correct' not in data:
            return validation_error_response('correct field is required')

        is_correct = bool(data['correct'])

        item.times_practiced += 1
        if is_correct:
            item.times_correct += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'times_practiced': item.times_practiced,
            'times_correct': item.times_correct,
            'accuracy_rate': item.accuracy_rate
        }), 200

    except Exception as e:
        logger.error(f"Error recording practice for item {item_id}: {e}")
        db.session.rollback()
        return error_response('Failed to record practice', 500, str(e))
