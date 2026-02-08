"""SQLAlchemy models for lesson-based learning platform

This module defines the database models for the Korean learning app v2.0,
transitioning from flashcards to a structured lesson-based curriculum.

Models:
- Course: Top-level course (e.g., "Korean Fundamentals")
- Unit: Section within a course (e.g., "Unit 1: Greetings")
- Lesson: Individual lesson with grammar explanation
- Exercise: Different types: vocabulary, grammar, reading, listening, review
- UserProgress: Completion tracking for lessons
- VocabularyItem: Glossary/reference vocabulary
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy import CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from database import db


class ExerciseType(str, Enum):
    """Types of exercises available in lessons"""

    VOCABULARY = "vocabulary"  # Vocabulary matching/translation
    GRAMMAR = "grammar"  # Fill-in-blank, grammar rules
    READING = "reading"  # Reading comprehension
    LISTENING = "listening"  # Audio comprehension
    WRITING = "writing"  # Free-form writing exercises
    REVIEW = "review"  # Mixed review exercises
    SENTENCE_ARRANGE = "sentence_arrange"  # Arrange words to form sentence


class Course(db.Model):
    """Top-level course containing units and lessons"""

    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(50), default="Korean")
    level: Mapped[str] = mapped_column(
        String(50), default="Beginner"
    )  # Beginner, Intermediate, Advanced
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    units: Mapped[List["Unit"]] = relationship(
        "Unit",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Unit.display_order",
    )

    def __repr__(self) -> str:
        return f"<Course {self.id}: {self.title}>"

    @property
    def unit_count(self) -> int:
        return len(self.units)

    @property
    def total_lessons(self) -> int:
        return sum(len(unit.lessons) for unit in self.units)


class Unit(db.Model):
    """Section within a course containing related lessons"""

    __tablename__ = "unit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("course.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # For progression gating

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="units")
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="Lesson.display_order",
    )

    __table_args__ = (Index("idx_unit_course_order", "course_id", "display_order"),)

    def __repr__(self) -> str:
        return f"<Unit {self.id}: {self.title}>"

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)


class Lesson(db.Model):
    """Individual lesson with grammar explanation and exercises"""

    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("unit.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Grammar content (Markdown supported)
    grammar_explanation: Mapped[Optional[str]] = mapped_column(Text)
    grammar_tip: Mapped[Optional[str]] = mapped_column(Text)  # Optional quick tip

    # Lesson metadata
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=5)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    unit: Mapped["Unit"] = relationship("Unit", back_populates="lessons")
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Exercise.display_order",
    )
    progress: Mapped[List["UserProgress"]] = relationship(
        "UserProgress", back_populates="lesson", cascade="all, delete-orphan"
    )
    grammar_patterns: Mapped[List["GrammarPattern"]] = relationship(
        "GrammarPattern",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="GrammarPattern.display_order",
    )

    __table_args__ = (Index("idx_lesson_unit_order", "unit_id", "display_order"),)

    def __repr__(self) -> str:
        return f"<Lesson {self.id}: {self.title}>"

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)


class Exercise(db.Model):
    """Individual exercise within a lesson"""

    __tablename__ = "exercise"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lesson.id"), nullable=False
    )

    # Exercise type and content
    exercise_type: Mapped[ExerciseType] = mapped_column(
        SQLEnum(ExerciseType), nullable=False
    )

    # Question/prompt
    question: Mapped[str] = mapped_column(Text, nullable=False)
    instruction: Mapped[Optional[str]] = mapped_column(
        Text
    )  # e.g., "Select the correct translation"

    # For vocabulary/grammar exercises
    korean_text: Mapped[Optional[str]] = mapped_column(Text)
    romanization: Mapped[Optional[str]] = mapped_column(Text)
    english_text: Mapped[Optional[str]] = mapped_column(Text)

    # Answer options (JSON string for multiple choice)
    options: Mapped[Optional[str]] = mapped_column(
        Text
    )  # JSON: ["option1", "option2", ...]
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)

    # For reading/listening exercises
    content_text: Mapped[Optional[str]] = mapped_column(
        Text
    )  # Reading passage or audio transcript
    audio_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Explanation shown after answering
    explanation: Mapped[Optional[str]] = mapped_column(Text)

    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Optional link to grammar pattern for mastery tracking
    grammar_pattern_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("grammar_pattern.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercises")
    grammar_pattern: Mapped[Optional["GrammarPattern"]] = relationship(
        "GrammarPattern", back_populates="exercises"
    )

    __table_args__ = (
        Index("idx_exercise_lesson_order", "lesson_id", "display_order"),
        Index("idx_exercise_type", "exercise_type"),
    )

    def __repr__(self) -> str:
        return f"<Exercise {self.id}: {self.exercise_type.value} in Lesson {self.lesson_id}>"


class UserProgress(db.Model):
    """Tracks user completion and performance on lessons"""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lesson.id"), nullable=False
    )

    # For multi-user support (optional, default user_id=1)
    user_id: Mapped[int] = mapped_column(Integer, default=1)

    # Progress tracking
    is_started: Mapped[bool] = mapped_column(Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_exercises: Mapped[int] = mapped_column(Integer, default=0)
    total_exercises: Mapped[int] = mapped_column(Integer, default=0)

    # Performance metrics
    score: Mapped[Optional[float]] = mapped_column(Float)  # Percentage score (0-100)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")

    __table_args__ = (
        Index("idx_user_lesson", "user_id", "lesson_id"),
        Index("idx_user_completed", "user_id", "is_completed"),
    )

    def __repr__(self) -> str:
        status = (
            "completed"
            if self.is_completed
            else ("started" if self.is_started else "not started")
        )
        return f"<UserProgress Lesson {self.lesson_id}: {status}>"


class VocabularyItem(db.Model):
    """Standalone vocabulary reference/glossary item"""

    __tablename__ = "vocabulary_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Word content
    korean: Mapped[str] = mapped_column(Text, nullable=False)
    romanization: Mapped[Optional[str]] = mapped_column(Text)
    english: Mapped[str] = mapped_column(Text, nullable=False)

    # Additional info
    part_of_speech: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # noun, verb, adjective, etc.
    example_sentence_korean: Mapped[Optional[str]] = mapped_column(Text)
    example_sentence_english: Mapped[Optional[str]] = mapped_column(Text)

    # Audio
    audio_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Categorization
    category: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # greetings, numbers, family, etc.
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-5

    # Tracking
    times_practiced: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)

    # Spaced Repetition (SM-2 algorithm)
    next_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    review_interval: Mapped[int] = mapped_column(Integer, default=1)  # Days until next review
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)  # SM-2 ease factor (min 1.3)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)  # Number of successful reviews

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_vocab_category", "category"),
        Index("idx_vocab_difficulty", "difficulty_level"),
        Index("idx_vocab_next_review", "next_review_date"),
        CheckConstraint(
            "difficulty_level >= 1 AND difficulty_level <= 5",
            name="check_vocab_difficulty",
        ),
    )

    def __repr__(self) -> str:
        return f"<VocabularyItem {self.id}: {self.korean} = {self.english}>"

    @property
    def accuracy_rate(self) -> Optional[float]:
        """Calculate accuracy rate if practiced"""
        if self.times_practiced == 0:
            return None
        return (self.times_correct / self.times_practiced) * 100


class GrammarPattern(db.Model):
    """Grammar pattern associated with a lesson for mastery tracking"""

    __tablename__ = "grammar_pattern"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lesson.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    meaning: Mapped[Optional[str]] = mapped_column(Text)
    example_korean: Mapped[Optional[str]] = mapped_column(Text)
    example_english: Mapped[Optional[str]] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="grammar_patterns")
    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="grammar_pattern"
    )
    mastery_records: Mapped[List["GrammarMastery"]] = relationship(
        "GrammarMastery", back_populates="pattern", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_grammar_pattern_lesson", "lesson_id", "display_order"),
    )

    def __repr__(self) -> str:
        return f"<GrammarPattern {self.id}: {self.title}>"


class GrammarMastery(db.Model):
    """Tracks user mastery of individual grammar patterns"""

    __tablename__ = "grammar_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    pattern_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("grammar_pattern.id"), nullable=False
    )

    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_practiced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    pattern: Mapped["GrammarPattern"] = relationship(
        "GrammarPattern", back_populates="mastery_records"
    )

    __table_args__ = (
        Index("idx_grammar_mastery_user_pattern", "user_id", "pattern_id", unique=True),
    )


class ExerciseSRS(db.Model):
    """Spaced repetition tracking for individual exercises (sentence-level SRS)"""

    __tablename__ = "exercise_srs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    exercise_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exercise.id"), nullable=False
    )

    # SM-2 fields
    next_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    review_interval: Mapped[int] = mapped_column(Integer, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)

    # Performance tracking
    times_practiced: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)

    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    exercise: Mapped["Exercise"] = relationship("Exercise", backref="srs_records")

    __table_args__ = (
        Index("idx_exercise_srs_user_exercise", "user_id", "exercise_id", unique=True),
        Index("idx_exercise_srs_next_review", "user_id", "next_review_date"),
    )
