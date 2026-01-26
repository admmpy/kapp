"""Pytest fixtures for Kapp backend tests"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from database import db
from models import Card, Deck, Review


class TestingConfig:
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    TTS_CACHE_DIR = 'data/audio_cache'
    LLM_CACHE_DIR = 'data/llm_cache'
    LLM_MODEL = 'test-model'
    LLM_BASE_URL = 'http://localhost:11434'
    LLM_ENABLED = False
    CORS_ORIGINS = ['http://localhost:5173']
    RATELIMIT_ENABLED = False


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config.from_object(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_deck(app):
    """Create a sample deck for testing"""
    with app.app_context():
        deck = Deck(
            name='Test Deck',
            description='A test deck',
            level=1
        )
        db.session.add(deck)
        db.session.commit()
        deck_id = deck.id
        yield deck_id


@pytest.fixture
def sample_card(app, sample_deck):
    """Create a sample card for testing"""
    with app.app_context():
        card = Card(
            deck_id=sample_deck,
            front_korean='안녕하세요',
            front_romanization='annyeonghaseyo',
            back_english='Hello',
            level=1,
            ease_factor=2.5,
            interval=0,
            repetitions=0
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id
        yield card_id


@pytest.fixture
def multiple_cards(app, sample_deck):
    """Create multiple cards for testing"""
    with app.app_context():
        cards = []
        test_data = [
            ('감사합니다', 'gamsahamnida', 'Thank you'),
            ('네', 'ne', 'Yes'),
            ('아니요', 'aniyo', 'No'),
        ]
        for korean, romanization, english in test_data:
            card = Card(
                deck_id=sample_deck,
                front_korean=korean,
                front_romanization=romanization,
                back_english=english,
                level=1,
                ease_factor=2.5,
                interval=0,
                repetitions=0
            )
            db.session.add(card)
            cards.append(card)
        db.session.commit()
        card_ids = [c.id for c in cards]
        yield card_ids
