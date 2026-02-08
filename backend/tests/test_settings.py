import pytest
from app import create_app
from database import db
from models_v2 import UserSettings

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_settings_default(client):
    """Test getting settings returns default values"""
    response = client.get('/api/settings')
    assert response.status_code == 200
    data = response.get_json()
    assert 'immersion_level' in data
    assert data['immersion_level'] == 1

def test_update_settings(client):
    """Test updating settings persists changes"""
    # Update to level 2
    response = client.put('/api/settings', json={'immersion_level': 2})
    assert response.status_code == 200
    data = response.get_json()
    assert data['immersion_level'] == 2

    # Verify persistence
    response = client.get('/api/settings')
    assert response.status_code == 200
    data = response.get_json()
    assert data['immersion_level'] == 2

def test_update_settings_invalid_input(client):
    """Test updating settings with invalid input"""
    # Invalid level (out of range)
    response = client.put('/api/settings', json={'immersion_level': 5})
    assert response.status_code == 400
    
    # Invalid type
    response = client.put('/api/settings', json={'immersion_level': 'invalid'})
    assert response.status_code == 400
