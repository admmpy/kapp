"""Pytest fixtures for Kapp backend tests"""
import json
import pytest
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from database import db as _db
from models_v2 import (
    Course, Unit, Lesson, Exercise, UserProgress,
    VocabularyItem, ExerciseType, GrammarPattern, GrammarMastery,
)


class TestingConfig:
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key-only-for-automated-testing-not-production"
    TTS_CACHE_DIR = "data/audio_cache"
    LLM_CACHE_DIR = "data/llm_cache"
    OPENAI_API_KEY = "test-openai-key"
    OPENAI_MODEL = "gpt-4o-mini"
    LLM_ENABLED = False
    CORS_ORIGINS = ["http://localhost:5173"]
    RATELIMIT_ENABLED = False
    GRAMMAR_MASTERY_ENABLED = False


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app("testing")
    app.config.from_object(TestingConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def app_with_mastery():
    """Create application with grammar mastery enabled"""
    app = create_app("testing")
    app.config.from_object(TestingConfig)
    app.config["GRAMMAR_MASTERY_ENABLED"] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def client_with_mastery(app_with_mastery):
    """Create test client with grammar mastery enabled"""
    return app_with_mastery.test_client()


@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        yield _db.session


@pytest.fixture
def sample_course(app):
    """Create a sample course with unit, lesson, and exercises"""
    with app.app_context():
        course = Course(title="Test Korean", language="Korean", level="Beginner")
        _db.session.add(course)
        _db.session.flush()

        unit = Unit(course_id=course.id, title="Test Unit", display_order=0)
        _db.session.add(unit)
        _db.session.flush()

        lesson = Lesson(
            unit_id=unit.id,
            title="Test Lesson",
            grammar_explanation="Test grammar",
            estimated_minutes=5,
            display_order=0,
        )
        _db.session.add(lesson)
        _db.session.flush()

        # Vocabulary exercise with audio
        ex1 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.VOCABULARY,
            question="What does 안녕하세요 mean?",
            instruction="Select the correct translation",
            korean_text="안녕하세요",
            audio_url="/api/audio/test.mp3",
            options=json.dumps(["Hello", "Goodbye", "Thank you", "Sorry"]),
            correct_answer="Hello",
            explanation="안녕하세요 means hello",
            display_order=0,
        )
        # Grammar exercise (no audio)
        ex2 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.GRAMMAR,
            question="Choose the correct goodbye",
            options=json.dumps(["안녕히 가세요", "안녕히 계세요", "안녕", "뭐야"]),
            correct_answer="안녕히 가세요",
            explanation="안녕히 가세요 when someone is leaving",
            display_order=1,
        )
        # Listening exercise with audio
        ex3 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.LISTENING,
            question="Listen and select",
            audio_url="/api/audio/test2.mp3",
            options=json.dumps(["안녕하세요", "감사합니다"]),
            correct_answer="안녕하세요",
            display_order=2,
        )
        # Reading exercise (no audio)
        ex4 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.READING,
            question="What does this passage say?",
            content_text="안녕하세요. 저는 학생입니다.",
            options=json.dumps(["Greeting", "Farewell"]),
            correct_answer="Greeting",
            display_order=3,
        )

        _db.session.add_all([ex1, ex2, ex3, ex4])
        _db.session.commit()

        yield {
            "course_id": course.id,
            "unit_id": unit.id,
            "lesson_id": lesson.id,
            "exercise_ids": [ex1.id, ex2.id, ex3.id, ex4.id],
        }


@pytest.fixture
def sample_course_with_patterns(app_with_mastery):
    """Create a sample course with grammar patterns linked to exercises"""
    with app_with_mastery.app_context():
        course = Course(title="Test Korean", language="Korean", level="Beginner")
        _db.session.add(course)
        _db.session.flush()

        unit = Unit(course_id=course.id, title="Test Unit", display_order=0)
        _db.session.add(unit)
        _db.session.flush()

        lesson = Lesson(
            unit_id=unit.id,
            title="Test Lesson",
            grammar_explanation="Test grammar",
            estimated_minutes=5,
            display_order=0,
        )
        _db.session.add(lesson)
        _db.session.flush()

        # Create grammar patterns
        pattern1 = GrammarPattern(
            lesson_id=lesson.id,
            key="formal_greeting",
            title="Formal Greeting",
            pattern="안녕하세요",
            meaning="Polite hello",
            example_korean="안녕하세요!",
            example_english="Hello!",
            display_order=0,
        )
        pattern2 = GrammarPattern(
            lesson_id=lesson.id,
            key="formal_apology",
            title="Formal Apology",
            pattern="죄송합니다",
            meaning="I'm sorry (formal)",
            example_korean="늦어서 죄송합니다.",
            example_english="I'm sorry for being late.",
            display_order=1,
        )
        _db.session.add_all([pattern1, pattern2])
        _db.session.flush()

        # Grammar exercise linked to pattern1
        ex1 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.GRAMMAR,
            question="How do you greet formally?",
            options=json.dumps(["안녕하세요", "안녕", "뭐야", "아니요"]),
            correct_answer="안녕하세요",
            explanation="안녕하세요 is the formal greeting",
            grammar_pattern_id=pattern1.id,
            display_order=0,
        )
        # Grammar exercise linked to pattern2
        ex2 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.GRAMMAR,
            question="How do you apologize formally?",
            options=json.dumps(["죄송합니다", "미안", "괜찮아요", "감사합니다"]),
            correct_answer="죄송합니다",
            explanation="죄송합니다 is the formal apology",
            grammar_pattern_id=pattern2.id,
            display_order=1,
        )
        # Exercise without pattern link
        ex3 = Exercise(
            lesson_id=lesson.id,
            exercise_type=ExerciseType.VOCABULARY,
            question="What does 감사합니다 mean?",
            options=json.dumps(["Thank you", "Hello", "Goodbye", "Sorry"]),
            correct_answer="Thank you",
            display_order=2,
        )

        _db.session.add_all([ex1, ex2, ex3])
        _db.session.commit()

        yield {
            "course_id": course.id,
            "unit_id": unit.id,
            "lesson_id": lesson.id,
            "exercise_ids": [ex1.id, ex2.id, ex3.id],
            "pattern_ids": [pattern1.id, pattern2.id],
        }
