"""Statistics endpoints

This blueprint provides learning progress and statistics data.

Endpoints:
- GET /api/stats - Get overall learning statistics
"""
from flask import Blueprint, jsonify, current_app
from sqlalchemy import select, func
from datetime import date, datetime, timedelta
from database import db
from models import Card, Review, Deck

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall learning statistics
    
    Returns:
        JSON with comprehensive learning statistics
    """
    try:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Total cards
        total_cards = db.session.execute(
            select(func.count()).select_from(Card)
        ).scalar()
        
        # Cards due today
        cards_due_today = db.session.execute(
            select(func.count()).select_from(Card).where(
                (Card.next_review_date == None) | (Card.next_review_date <= today)
            )
        ).scalar()
        
        # New cards (never reviewed)
        new_cards = db.session.execute(
            select(func.count()).select_from(Card).where(Card.repetitions == 0)
        ).scalar()
        
        # Cards reviewed today
        cards_reviewed_today = db.session.execute(
            select(func.count()).select_from(Review).where(
                Review.review_date >= today_start
            )
        ).scalar()
        
        # Total reviews
        total_reviews = db.session.execute(
            select(func.count()).select_from(Review)
        ).scalar()
        
        # Calculate accuracy rate (percentage of reviews with rating >= 3)
        if total_reviews > 0:
            successful_reviews = db.session.execute(
                select(func.count()).select_from(Review).where(Review.quality_rating >= 3)
            ).scalar()
            accuracy_rate = round((successful_reviews / total_reviews) * 100, 1)
        else:
            accuracy_rate = 0.0
        
        # Calculate review streak (consecutive days with reviews)
        streak_days = calculate_review_streak()
        
        # Get deck statistics
        decks = db.session.execute(select(Deck)).scalars().all()
        deck_stats = []
        for deck in decks:
            deck_card_count = db.session.execute(
                select(func.count()).select_from(Card).where(Card.deck_id == deck.id)
            ).scalar()
            
            deck_due_count = db.session.execute(
                select(func.count()).select_from(Card).where(
                    Card.deck_id == deck.id,
                    (Card.next_review_date == None) | (Card.next_review_date <= today)
                )
            ).scalar()
            
            deck_stats.append({
                'id': deck.id,
                'name': deck.name,
                'level': deck.level,
                'total_cards': deck_card_count,
                'due_cards': deck_due_count
            })
        
        return jsonify({
            'total_cards': total_cards,
            'cards_due_today': cards_due_today,
            'new_cards': new_cards,
            'cards_reviewed_today': cards_reviewed_today,
            'total_reviews': total_reviews,
            'accuracy_rate': accuracy_rate,
            'streak_days': streak_days,
            'decks': deck_stats
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch statistics'}), 500


def calculate_review_streak() -> int:
    """Calculate consecutive days with reviews
    
    Returns:
        Number of consecutive days with at least one review
    """
    try:
        streak = 0
        current_date = date.today()
        
        # Check each day going backwards
        while True:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            # Check if any reviews exist for this day
            review_count = db.session.execute(
                select(func.count()).select_from(Review).where(
                    Review.review_date >= day_start,
                    Review.review_date < day_end
                )
            ).scalar()
            
            if review_count == 0:
                # Streak broken
                break
            
            streak += 1
            current_date -= timedelta(days=1)
            
            # Limit to 365 days to avoid infinite loops
            if streak >= 365:
                break
        
        return streak
    
    except Exception as e:
        current_app.logger.error(f"Error calculating streak: {e}")
        return 0


@stats_bp.route('/stats/recent-reviews', methods=['GET'])
def get_recent_reviews():
    """Get recent review activity
    
    Returns:
        JSON with recent reviews (last 50)
    """
    try:
        reviews = Review.query\
            .order_by(Review.review_date.desc())\
            .limit(50)\
            .all()
        
        reviews_data = []
        for review in reviews:
            card = db.session.get(Card, review.card_id)
            reviews_data.append({
                'id': review.id,
                'card_id': review.card_id,
                'card_korean': card.front_korean if card else None,
                'card_english': card.back_english if card else None,
                'review_date': review.review_date.isoformat(),
                'quality_rating': review.quality_rating,
                'time_spent': review.time_spent,
                'was_successful': review.was_successful
            })
        
        return jsonify({
            'reviews': reviews_data,
            'count': len(reviews_data)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error fetching recent reviews: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch recent reviews'}), 500
