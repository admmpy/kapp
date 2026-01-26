"""Card CRUD endpoints

This blueprint handles flashcard retrieval and management.

Endpoints:
- GET /api/cards/due - Get cards due for review today
- GET /api/cards/:id - Get specific card details
- GET /api/cards - Get all cards (with pagination)
"""
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select
from datetime import date
from database import db
from models import Card, Deck
from tts_service import get_tts_service
from utils import error_response, not_found_response

cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/cards/due', methods=['GET'])
def get_due_cards():
    """Get all cards due for review today
    
    Query parameters:
        level: Filter by card level (0-5)
        deck_id: Filter by deck ID
        limit: Maximum number of cards to return (default 20)
    
    Returns:
        JSON with list of due cards and metadata
    """
    try:
        # Get query parameters
        level = request.args.get('level', type=int)
        deck_id = request.args.get('deck_id', type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Build query for due cards
        query = select(Card).where(
            (Card.next_review_date == None) | (Card.next_review_date <= date.today())
        )
        
        # Apply filters
        if level is not None:
            query = query.where(Card.level == level)
        if deck_id is not None:
            query = query.where(Card.deck_id == deck_id)
        
        # Order by next_review_date (oldest first), then by ID
        query = query.order_by(Card.next_review_date.asc().nullsfirst(), Card.id)
        
        # Limit results
        query = query.limit(limit)
        
        # Execute query
        cards = db.session.execute(query).scalars().all()
        
        # Get TTS service
        tts_service = get_tts_service(current_app.config['TTS_CACHE_DIR'])
        
        # Generate audio for cards and serialize
        cards_data = []
        for card in cards:
            # Generate audio (uses cache if available)
            audio_filename = tts_service.generate_audio(
                text=card.front_korean,
                lang='ko',
                slow=(card.level <= 1)  # Slow for beginner cards
            )
            
            cards_data.append({
                'id': card.id,
                'deck_id': card.deck_id,
                'front_korean': card.front_korean,
                'front_romanization': card.front_romanization,
                'back_english': card.back_english,
                'example_sentence': card.example_sentence,
                'level': card.level,
                'audio_url': tts_service.get_audio_url(audio_filename) if audio_filename else None,
                'is_new': card.is_new,
                'interval': card.interval,
                'repetitions': card.repetitions
            })
        
        return jsonify({
            'cards': cards_data,
            'total_due': len(cards_data),
            'limit': limit
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching due cards: {e}", exc_info=True)
        return error_response('Failed to fetch due cards', 500)


@cards_bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    """Get specific card by ID
    
    Args:
        card_id: Card ID
    
    Returns:
        JSON with card details
    """
    try:
        card = db.session.get(Card, card_id)
        
        if not card:
            return not_found_response('Card')
        
        # Get TTS service and generate audio
        tts_service = get_tts_service(current_app.config['TTS_CACHE_DIR'])
        audio_filename = tts_service.generate_audio(
            text=card.front_korean,
            lang='ko',
            slow=(card.level <= 1)
        )
        
        return jsonify({
            'id': card.id,
            'deck_id': card.deck_id,
            'front_korean': card.front_korean,
            'front_romanization': card.front_romanization,
            'back_english': card.back_english,
            'example_sentence': card.example_sentence,
            'level': card.level,
            'interval': card.interval,
            'repetitions': card.repetitions,
            'ease_factor': card.ease_factor,
            'next_review_date': card.next_review_date.isoformat() if card.next_review_date else None,
            'audio_url': tts_service.get_audio_url(audio_filename) if audio_filename else None,
            'is_new': card.is_new,
            'is_due': card.is_due
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching card {card_id}: {e}", exc_info=True)
        return error_response('Failed to fetch card', 500)


@cards_bp.route('/cards', methods=['GET'])
def get_all_cards():
    """Get all cards with pagination
    
    Query parameters:
        page: Page number (default 1)
        per_page: Items per page (default 50)
        deck_id: Filter by deck ID
        level: Filter by level
    
    Returns:
        JSON with paginated cards list
    """
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=50, type=int)
        deck_id = request.args.get('deck_id', type=int)
        level = request.args.get('level', type=int)
        
        # Build query
        query = select(Card)
        
        if deck_id is not None:
            query = query.where(Card.deck_id == deck_id)
        if level is not None:
            query = query.where(Card.level == level)
        
        query = query.order_by(Card.id)
        
        # Get total count
        total_count = db.session.execute(
            select(db.func.count()).select_from(Card)
        ).scalar()
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.limit(per_page).offset(offset)
        
        cards = db.session.execute(query).scalars().all()
        
        cards_data = [{
            'id': card.id,
            'deck_id': card.deck_id,
            'front_korean': card.front_korean,
            'front_romanization': card.front_romanization,
            'back_english': card.back_english,
            'level': card.level,
            'is_new': card.is_new,
            'is_due': card.is_due
        } for card in cards]
        
        return jsonify({
            'cards': cards_data,
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': (total_count + per_page - 1) // per_page
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching cards: {e}", exc_info=True)
        return error_response('Failed to fetch cards', 500)
