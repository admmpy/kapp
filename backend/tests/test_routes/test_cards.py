"""Tests for card API endpoints"""
import pytest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


class TestGetDueCards:
    """Test GET /api/cards/due endpoint"""

    def test_returns_due_cards(self, client, sample_card):
        """Should return cards that are due for review"""
        response = client.get('/api/cards/due')
        assert response.status_code == 200
        data = response.get_json()
        assert 'cards' in data
        assert 'total_due' in data

    def test_returns_empty_when_no_cards(self, client):
        """Should return empty list when no cards exist"""
        response = client.get('/api/cards/due')
        assert response.status_code == 200
        data = response.get_json()
        assert data['cards'] == []
        assert data['total_due'] == 0

    def test_respects_limit_parameter(self, client, multiple_cards):
        """Should respect limit query parameter"""
        response = client.get('/api/cards/due?limit=2')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cards']) <= 2

    def test_filters_by_level(self, client, sample_card):
        """Should filter cards by level"""
        response = client.get('/api/cards/due?level=1')
        assert response.status_code == 200
        data = response.get_json()
        for card in data['cards']:
            assert card['level'] == 1

    def test_filters_by_deck_id(self, client, sample_card, sample_deck):
        """Should filter cards by deck_id"""
        response = client.get(f'/api/cards/due?deck_id={sample_deck}')
        assert response.status_code == 200
        data = response.get_json()
        for card in data['cards']:
            assert card['deck_id'] == sample_deck

    def test_card_has_expected_fields(self, client, sample_card):
        """Returned cards should have all expected fields"""
        response = client.get('/api/cards/due')
        assert response.status_code == 200
        data = response.get_json()
        if data['cards']:
            card = data['cards'][0]
            expected_fields = [
                'id', 'deck_id', 'front_korean', 'front_romanization',
                'back_english', 'level', 'is_new', 'interval', 'repetitions'
            ]
            for field in expected_fields:
                assert field in card, f"Missing field: {field}"


class TestGetCard:
    """Test GET /api/cards/:id endpoint"""

    def test_returns_card_by_id(self, client, sample_card):
        """Should return card details by ID"""
        response = client.get(f'/api/cards/{sample_card}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_card

    def test_returns_404_for_nonexistent_card(self, client):
        """Should return 404 for non-existent card"""
        response = client.get('/api/cards/99999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_card_details_include_scheduling_info(self, client, sample_card):
        """Card details should include SM-2 scheduling info"""
        response = client.get(f'/api/cards/{sample_card}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'interval' in data
        assert 'repetitions' in data
        assert 'ease_factor' in data
        assert 'next_review_date' in data


class TestGetAllCards:
    """Test GET /api/cards endpoint"""

    def test_returns_paginated_cards(self, client, multiple_cards):
        """Should return paginated list of all cards"""
        response = client.get('/api/cards')
        assert response.status_code == 200
        data = response.get_json()
        assert 'cards' in data
        assert 'page' in data
        assert 'per_page' in data
        assert 'total_count' in data
        assert 'total_pages' in data

    def test_respects_pagination_parameters(self, client, multiple_cards):
        """Should respect page and per_page parameters"""
        response = client.get('/api/cards?page=1&per_page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cards']) <= 2
        assert data['page'] == 1
        assert data['per_page'] == 2

    def test_filters_by_deck_id(self, client, sample_card, sample_deck):
        """Should filter by deck_id"""
        response = client.get(f'/api/cards?deck_id={sample_deck}')
        assert response.status_code == 200
        data = response.get_json()
        for card in data['cards']:
            assert card['deck_id'] == sample_deck

    def test_filters_by_level(self, client, sample_card):
        """Should filter by level"""
        response = client.get('/api/cards?level=1')
        assert response.status_code == 200
        data = response.get_json()
        for card in data['cards']:
            assert card['level'] == 1
