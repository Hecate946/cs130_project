import pytest
from flask import Flask
from routes import api  # Import the Flask Blueprint
from database.db import db  # Import the SQLAlchemy instance

@pytest.fixture
def client():
    """Fixture to create a test client for Flask"""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(api)  # Register the API blueprint
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# ------------------ Gym API Tests ------------------


def test_get_specific_gym(client):
    """Test fetching a specific gym"""
    response = client.get("/v1/gym/bfit")  # Assuming 'bfit' is a valid gym
    assert response.status_code in [200, 404]
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert data["data"]["slug"] == "bfit"
    else:
        assert "error" in data


def test_get_invalid_gym(client):
    """Test fetching an invalid gym"""
    response = client.get("/v1/gym/invalid-gym")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Gym not found"


# ------------------ Dining API Tests ------------------


def test_get_specific_dining_hall(client):
    """Test fetching a specific dining hall"""
    response = client.get(
        "/v1/dining/epicuria")  # Assuming 'epicuria' is a valid slug
    assert response.status_code in [200, 404]
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert data["data"]["slug"] == "epicuria"
    else:
        assert "error" in data


def test_get_invalid_dining_hall(client):
    """Test fetching an invalid dining hall"""
    response = client.get("/v1/dining/non-existent-hall")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Dining hall not found"
