"""Statistics endpoints

This blueprint provides learning progress and statistics data.

Endpoints:
- GET /api/stats - Get overall learning statistics

Response includes:
- cards_due_today: int
- total_cards: int
- cards_reviewed_today: int
- accuracy_rate: float
- streak_days: int

TODO: Implement GET /api/stats endpoint
TODO: Calculate cards due today
TODO: Calculate accuracy rate from reviews
TODO: Track daily review streak
TODO: Add caching for expensive queries
"""
