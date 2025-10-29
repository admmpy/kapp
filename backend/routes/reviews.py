"""Review submission endpoints

This blueprint handles user review submissions and SM-2 scheduling updates.

Endpoints:
- POST /api/reviews - Submit review for a card

Request body:
- card_id: int
- quality_rating: int (0-5)
- time_spent: float (seconds)

TODO: Implement POST /api/reviews endpoint
TODO: Validate quality_rating range (0-5)
TODO: Calculate new SM-2 parameters
TODO: Update card's next_review_date
TODO: Record review in database
"""
