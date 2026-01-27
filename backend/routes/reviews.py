"""Review submission endpoints

This blueprint handles user review submissions and SM-2 scheduling updates.

Endpoints:
- POST /api/reviews - Submit review for a card
"""
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from database import db
from models import Card, Review
from srs import update_card_after_review
from utils import error_response, not_found_response, validation_error_response

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/reviews", methods=["POST"])
def submit_review():
    """Submit a review for a card

    Request body (JSON):
        card_id: int - ID of the card being reviewed
        quality_rating: int - User's rating (0-5)
        time_spent: float - Time spent on card in seconds (optional)

    Returns:
        JSON with updated card scheduling info
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or "card_id" not in data or "quality_rating" not in data:
            return validation_error_response(
                "Missing required fields: card_id, quality_rating"
            )

        card_id = data["card_id"]
        quality_rating = data["quality_rating"]
        time_spent = data.get("time_spent")

        # Validate quality rating
        if not isinstance(quality_rating, int) or not 0 <= quality_rating <= 5:
            return validation_error_response(
                "quality_rating must be an integer between 0 and 5"
            )

        # Get card
        card = db.session.get(Card, card_id)
        if not card:
            return not_found_response("Card")

        # Create review record
        review = Review(
            card_id=card_id,
            review_date=datetime.utcnow(),
            quality_rating=quality_rating,
            time_spent=time_spent,
        )
        db.session.add(review)

        # Update card with SM-2 algorithm
        update_card_after_review(card, quality_rating)

        # Commit changes
        db.session.commit()

        current_app.logger.info(
            f"Review submitted: Card {card_id}, Rating {quality_rating}, "
            f"Next review: {card.next_review_date}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "card_id": card.id,
                    "next_review_date": card.next_review_date.isoformat(),
                    "interval": card.interval,
                    "repetitions": card.repetitions,
                    "ease_factor": round(card.ease_factor, 2),
                }
            ),
            201,
        )

    except ValueError as e:
        db.session.rollback()
        return validation_error_response(str(e))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting review: {e}", exc_info=True)
        return error_response("Failed to submit review", 500)


@reviews_bp.route("/reviews/card/<int:card_id>", methods=["GET"])
def get_card_reviews(card_id):
    """Get review history for a specific card

    Args:
        card_id: Card ID

    Returns:
        JSON with list of reviews for the card
    """
    try:
        # Check if card exists
        card = db.session.get(Card, card_id)
        if not card:
            return not_found_response("Card")

        # Get reviews ordered by date (newest first)
        reviews = (
            Review.query.filter_by(card_id=card_id)
            .order_by(Review.review_date.desc())
            .all()
        )

        reviews_data = [
            {
                "id": review.id,
                "review_date": review.review_date.isoformat(),
                "quality_rating": review.quality_rating,
                "time_spent": review.time_spent,
                "was_successful": review.was_successful,
            }
            for review in reviews
        ]

        return jsonify(
            {
                "card_id": card_id,
                "reviews": reviews_data,
                "total_reviews": len(reviews_data),
            }
        )

    except Exception as e:
        current_app.logger.error(
            f"Error fetching reviews for card {card_id}: {e}", exc_info=True
        )
        return error_response("Failed to fetch reviews", 500)
