"""SQLAlchemy models for Card, Review, and Deck

This module defines the database models for the Korean learning app.

Models:
- Card: Flashcard with Korean text, romanization, English translation
- Review: Record of user review sessions with quality ratings
- Deck: Collection of related cards (e.g., "Greetings", "Numbers")

TODO: Define Card model with SM-2 fields (interval, ease_factor, etc.)
TODO: Define Review model with quality_rating and time_spent
TODO: Define Deck model with card relationships
TODO: Add __repr__ methods for debugging
TODO: Create database indexes for performance
"""
