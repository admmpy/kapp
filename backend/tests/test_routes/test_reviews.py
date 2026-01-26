"""Tests for review API endpoints"""
import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


class TestSubmitReview:
    """Test POST /api/reviews endpoint"""

    def test_submits_review_successfully(self, client, sample_card):
        """Should successfully submit a review"""
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['card_id'] == sample_card
        assert 'next_review_date' in data
        assert 'interval' in data
        assert 'repetitions' in data
        assert 'ease_factor' in data

    def test_returns_400_without_card_id(self, client):
        """Should return 400 when card_id is missing"""
        response = client.post('/api/reviews', json={
            'quality_rating': 4
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_returns_400_without_quality_rating(self, client, sample_card):
        """Should return 400 when quality_rating is missing"""
        response = client.post('/api/reviews', json={
            'card_id': sample_card
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_returns_400_for_invalid_quality_rating(self, client, sample_card):
        """Should return 400 for quality_rating outside 0-5"""
        # Test too high
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 6
        })
        assert response.status_code == 400

        # Test too low
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': -1
        })
        assert response.status_code == 400

    def test_returns_404_for_nonexistent_card(self, client):
        """Should return 404 when card doesn't exist"""
        response = client.post('/api/reviews', json={
            'card_id': 99999,
            'quality_rating': 4
        })
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_accepts_time_spent(self, client, sample_card):
        """Should accept optional time_spent field"""
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4,
            'time_spent': 10.5
        })
        assert response.status_code == 201

    def test_updates_card_scheduling(self, client, sample_card):
        """Review should update card scheduling parameters"""
        # First review
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['repetitions'] == 1
        assert data['interval'] == 1

        # Second review
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['repetitions'] == 2
        assert data['interval'] == 6

    def test_failed_review_resets_progress(self, client, sample_card):
        """Failed review (quality < 3) should reset progress"""
        # First do successful review
        client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4
        })

        # Then fail
        response = client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 1
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['repetitions'] == 0
        assert data['interval'] == 1

    def test_all_quality_ratings_valid(self, client, sample_card, app):
        """All quality ratings 0-5 should be valid"""
        from database import db
        from models import Card

        for quality in range(6):
            # Reset card for each test
            with app.app_context():
                card = db.session.get(Card, sample_card)
                card.repetitions = 0
                card.interval = 0
                card.ease_factor = 2.5
                db.session.commit()

            response = client.post('/api/reviews', json={
                'card_id': sample_card,
                'quality_rating': quality
            })
            assert response.status_code == 201, f"Quality {quality} should be valid"


class TestGetCardReviews:
    """Test GET /api/reviews/card/:id endpoint"""

    def test_returns_review_history(self, client, sample_card):
        """Should return review history for a card"""
        # Submit a review first
        client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4
        })

        response = client.get(f'/api/reviews/card/{sample_card}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'reviews' in data
        assert 'total_reviews' in data
        assert data['card_id'] == sample_card

    def test_returns_404_for_nonexistent_card(self, client):
        """Should return 404 for non-existent card"""
        response = client.get('/api/reviews/card/99999')
        assert response.status_code == 404

    def test_returns_empty_list_for_no_reviews(self, client, sample_card):
        """Should return empty list when card has no reviews"""
        response = client.get(f'/api/reviews/card/{sample_card}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['reviews'] == []
        assert data['total_reviews'] == 0

    def test_review_has_expected_fields(self, client, sample_card):
        """Reviews should have expected fields"""
        # Submit a review first
        client.post('/api/reviews', json={
            'card_id': sample_card,
            'quality_rating': 4,
            'time_spent': 5.0
        })

        response = client.get(f'/api/reviews/card/{sample_card}')
        assert response.status_code == 200
        data = response.get_json()
        if data['reviews']:
            review = data['reviews'][0]
            assert 'id' in review
            assert 'review_date' in review
            assert 'quality_rating' in review
            assert 'was_successful' in review
