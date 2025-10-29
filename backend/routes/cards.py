"""Card CRUD endpoints

This blueprint handles flashcard retrieval and management.

Endpoints:
- GET /api/cards/due - Get cards due for review today
- GET /api/cards/:id - Get specific card details
- GET /api/cards - Get all cards (with pagination)

TODO: Implement GET /api/cards/due endpoint
TODO: Add query filtering by level and deck
TODO: Return cards with audio URLs
TODO: Include metadata (total_due, next_review_date)
"""
