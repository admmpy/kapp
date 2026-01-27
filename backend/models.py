"""SQLAlchemy models for Card, Review, and Deck

This module defines the database models for the Korean learning app.

Models:
- Card: Flashcard with Korean text, romanization, English translation
- Review: Record of user review sessions with quality ratings
- Deck: Collection of related cards (e.g., "Greetings", "Numbers")
"""
from datetime import datetime, date
from sqlalchemy import (
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Date,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from database import db


class Deck(db.Model):
    """Collection of related flashcards (e.g., 'Greetings', 'Numbers')"""

    __tablename__ = "deck"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[int] = mapped_column(
        Integer, default=0
    )  # TOPIK level (0=beginner, 1=A1, etc.)

    # Relationships
    cards: Mapped[List["Card"]] = relationship(
        "Card", back_populates="deck", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Deck {self.name} (Level {self.level})>"

    @property
    def card_count(self) -> int:
        """Return number of cards in this deck"""
        return len(self.cards)


class Card(db.Model):
    """Flashcard with Korean text, English translation, and SM-2 scheduling data"""

    __tablename__ = "card"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Foreign key
    deck_id: Mapped[int] = mapped_column(Integer, ForeignKey("deck.id"), nullable=False)

    # Card content
    front_korean: Mapped[str] = mapped_column(Text, nullable=False)
    front_romanization: Mapped[Optional[str]] = mapped_column(Text)
    back_english: Mapped[str] = mapped_column(Text, nullable=False)
    example_sentence: Mapped[Optional[str]] = mapped_column(Text)

    # Difficulty level
    level: Mapped[int] = mapped_column(
        Integer, default=0
    )  # 0-5 for progressive difficulty

    # SM-2 Algorithm fields
    interval: Mapped[int] = mapped_column(Integer, default=0)  # Days until next review
    repetitions: Mapped[int] = mapped_column(
        Integer, default=0
    )  # Number of successful reviews
    ease_factor: Mapped[float] = mapped_column(
        Float, default=2.5
    )  # Ease factor (min 1.3)
    next_review_date: Mapped[Optional[date]] = mapped_column(
        Date, index=True
    )  # When to review next

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="card", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("level >= 0 AND level <= 5", name="check_card_level"),
        CheckConstraint("ease_factor >= 1.3", name="check_ease_factor"),
        Index("idx_deck_level", "deck_id", "level"),
        Index("idx_next_review", "next_review_date"),
    )

    def __repr__(self) -> str:
        return f"<Card {self.id}: {self.front_korean} = {self.back_english}>"

    @property
    def is_new(self) -> bool:
        """Check if card has never been reviewed"""
        return self.repetitions == 0

    @property
    def is_due(self) -> bool:
        """Check if card is due for review today"""
        if self.next_review_date is None:
            return True
        return self.next_review_date <= date.today()


class Review(db.Model):
    """Record of a single review session for a card"""

    __tablename__ = "review"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Foreign key
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("card.id"), nullable=False)

    # Review data
    review_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    quality_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-5 scale
    time_spent: Mapped[Optional[float]] = mapped_column(Float)  # Seconds spent on card

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="reviews")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "quality_rating >= 0 AND quality_rating <= 5", name="check_quality_rating"
        ),
        Index("idx_review_date", "review_date"),
        Index("idx_card_review", "card_id", "review_date"),
    )

    def __repr__(self) -> str:
        return f"<Review {self.id}: Card {self.card_id}, Rating {self.quality_rating}>"

    @property
    def was_successful(self) -> bool:
        """Check if review was successful (rating >= 3)"""
        return self.quality_rating >= 3
