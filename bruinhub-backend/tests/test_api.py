import pytest
from config import FACILITY_IDS, OCCUSPACE_IDS
from database.db import db  # Import the SQLAlchemy instance
from flask import Flask
from routes import api  # Import the Flask Blueprint
from models.dining import DiningHall, DiningCapacityHistory  # Add these
from models.gyms import Gym, GymCapacityHistory  # Add these
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


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
        
        # Create test data for dining halls
        for slug in OCCUSPACE_IDS:
            hall = DiningHall(
                slug=slug,
                menu={"Breakfast": ["Test Food"]},
                hours_today={"open": "8:00 AM", "close": "8:00 PM"},
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(hall)
        
        # Create test data for gyms
        for slug in FACILITY_IDS:
            gym = Gym(
                slug=slug,
                regular_hours={"Monday": "6:00 AM - 10:00 PM"},
                special_hours={"2025-01-01": "CLOSED"},
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(gym)
        
        # Commit to save the data
        db.session.commit()
        
        # Add capacity data for dining halls
        for slug in OCCUSPACE_IDS:
            hall = DiningHall.query.filter_by(slug=slug).first()
            if hall:
                capacity = DiningCapacityHistory(
                    hall_id=hall.id,
                    occupants=50,
                    capacity=200,
                    last_updated=datetime.now(timezone.utc)
                )
                db.session.add(capacity)
        
        # Add capacity data for gyms
        for slug in FACILITY_IDS:
            gym = Gym.query.filter_by(slug=slug).first()
            if gym:
                for zone_name in ["Weight Room", "Cardio Area"]:
                    capacity = GymCapacityHistory(
                        gym_id=gym.id,
                        zone_name=zone_name,
                        occupants=30,
                        capacity=100,
                        last_updated=datetime.now(timezone.utc)
                    )
                    db.session.add(capacity)
        
        db.session.commit()
        
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
    response = client.get("/v1/dining/epicuria")  # Assuming 'epicuria' is a valid slug
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


# ------------------ Hours and Occupany API Tests ------------------


def test_get_occupancy(client):
    """Test fetching occupancy data"""
    response = client.get("/v1/hours-and-occupancy")
    assert response.status_code == 200
    data = response.get_json()
    
    assert "data" in data
    assert "timestamp" in data
    
    for facility in data["data"]:
        # Gyms
        if facility in FACILITY_IDS:
            assert "hours" in data["data"][facility]
            zone_count = 0
            for key in data["data"][facility]:
                if key != "hours":
                    zone_count += 1
                    assert "occupants" in data["data"][facility][key]
                    assert "capacity" in data["data"][facility][key]
            # Ensure we found at least one zone
            assert zone_count > 0, f"No zones found for gym {facility}"
                    
        # Dining halls
        elif facility in OCCUSPACE_IDS:
            assert "hours" in data["data"][facility]
            assert "occupants" in data["data"][facility]
            assert "capacity" in data["data"][facility]
        else:
            assert False, f"Unknown facility: {facility}"


@patch('routes.dining.dining_db')
def test_get_dining_halls(mock_dining_db, client):
    """Test GET /v1/dining endpoint"""
    # Setup mock
    mock_dining_db.get_dining_hall_latest.return_value = {
        "slug": "bplate",
        "menu": {"Breakfast": ["Eggs"]},
        "hours_today": {"open": "7:00 AM", "close": "9:00 PM"},
        "occupants": 50,
        "capacity": 200,
        "last_updated": datetime.now().isoformat()
    }
    
    # Make request
    response = client.get("/v1/dining")
    
    # Assertions
    assert response.status_code == 200
    assert "data" in response.json
    assert "bplate" in response.json["data"]

@patch('routes.dining.dining_db')
def test_get_specific_dining_hall(mock_dining_db, client):
    """Test GET /v1/dining/{slug} endpoint"""
    # Setup mock
    mock_dining_db.get_dining_hall_latest.return_value = {
        "slug": "bplate",
        "menu": {"Breakfast": ["Eggs"]},
        "hours_today": {"open": "7:00 AM", "close": "9:00 PM"},
        "occupants": 50,
        "capacity": 200,
        "last_updated": datetime.now().isoformat()
    }
    
    # Make request
    response = client.get("/v1/dining/bplate")
    
    # Assertions
    assert response.status_code == 200
    assert "data" in response.json
    assert response.json["data"]["slug"] == "bplate"

@patch('routes.historical.dining_db')
def test_historical_dining_data(mock_dining_db, client):
    """Test GET /v1/historical/dining/{slug} endpoint"""
    # Setup mock
    mock_dining_db.get_historical_capacity.return_value = {
        8: {"occupants": 25.5, "capacity": 200.0},
        9: {"occupants": 50.2, "capacity": 200.0},
        10: {"occupants": 75.8, "capacity": 200.0}
    }
    
    # Make request
    response = client.get("/v1/historical/dining/bplate")
    
    # Assertions
    assert response.status_code == 200
    assert "data" in response.json
    # Use string keys since JSON converts integer keys to strings
    assert "8" in response.json["data"]
    assert "occupants" in response.json["data"]["8"]
    assert response.json["data"]["8"]["occupants"] == 25.5

@patch('routes.hours_and_occupancy.dining_db')
def test_hours_and_occupancy(mock_dining_db, client):
    """Test GET /v1/hours-and-occupancy endpoint"""
    # Setup mocks for dining_db
    mock_capacity = MagicMock()
    mock_capacity.occupants = 50
    mock_capacity.capacity = 200
    mock_dining_db.get_latest_dining_capacity.return_value = mock_capacity
    
    mock_dining_db.get_dining_hall_latest.return_value = {
        "slug": "bplate",
        "menu": {"Breakfast": ["Eggs"]},
        "hours_today": {"open": "7:00 AM", "close": "9:00 PM"},
        "last_updated": datetime.now().isoformat()
    }
    
    # Make request
    response = client.get("/v1/hours-and-occupancy")
    
    # Assertions
    assert response.status_code == 200
    assert "data" in response.json


# ------------------ Library API Tests ------------------

@patch('routes.library.library_db')
def test_get_libraries(mock_library_db, client):
    """Test fetching all libraries"""
    # Setup mock
    mock_library_db.get_all_libraries.return_value = [
        {
            "slug": "powell",
            "name": "Powell Library",
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        {
            "slug": "yrl",
            "name": "Young Research Library",
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    response = client.get("/v1/library")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) == 2
    assert any(lib["slug"] == "powell" for lib in data["data"])


@patch('routes.library.library_db')
def test_get_specific_library(mock_library_db, client):
    """Test fetching a specific library"""
    # Setup mock - use get_library_details instead of get_library
    mock_library_db.get_library_details.return_value = {
        "slug": "powell",
        "name": "Powell Library",
        "hours_today": {"open": "8:00 AM", "close": "10:00 PM"},
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.get("/v1/library/powell")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert data["data"]["slug"] == "powell"


@patch('routes.library.library_db')
def test_get_library_bookings(mock_library_db, client):
    """Test fetching library bookings"""
    # Setup mock - use get_library_bookings_by_date_range instead of get_bookings_in_range
    mock_bookings = [
        {
            "id": 1,
            "room_id": 101,
            "start_time": "2025-03-08T14:00:00",
            "end_time": "2025-03-08T15:00:00",
            "status": "available"
        },
        {
            "id": 2,
            "room_id": 102,
            "start_time": "2025-03-08T15:00:00",
            "end_time": "2025-03-08T16:00:00",
            "status": "booked"
        }
    ]
    mock_library_db.get_library_bookings_by_date_range.return_value = mock_bookings
    
    response = client.get("/v1/library/powell/bookings/range?start=2025-03-08T00:00:00&end=2025-03-08T23:59:59")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) == 2
    assert data["data"][0]["room_id"] == 101


# ------------------ Historical Data API Tests ------------------

@patch('routes.historical.gym_db')
def test_historical_gym_data(mock_gym_db, client):
    """Test fetching historical gym data"""
    # Setup mock
    mock_gym_db.get_historical_capacity.return_value = {
        "Weight Room": {
            8: {"occupants": 15.0, "capacity": 50.0},
            9: {"occupants": 25.0, "capacity": 50.0},
            10: {"occupants": 35.0, "capacity": 50.0}
        },
        "Cardio Area": {
            8: {"occupants": 10.0, "capacity": 40.0},
            9: {"occupants": 20.0, "capacity": 40.0},
            10: {"occupants": 30.0, "capacity": 40.0}
        }
    }
    
    response = client.get("/v1/historical/gym/bfit")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "Weight Room" in data["data"]
    assert "8" in data["data"]["Weight Room"]
    assert data["data"]["Weight Room"]["8"]["occupants"] == 15.0


# ------------------ Error Handling Tests ------------------

def test_api_not_found(client):
    """Test 404 error for non-existent endpoint"""
    response = client.get("/v1/nonexistent-endpoint")
    assert response.status_code == 404
    # The response might not have JSON content, so we need to check that too
    data = response.get_json(silent=True)
    if data is not None:
        assert "error" in data
    # If no JSON is returned, we still want to ensure the status code is correct


@patch('routes.library.library_db')
def test_library_booking_missing_parameters(mock_library_db, client):
    """Test error handling for missing query parameters"""
    response = client.get("/v1/library/powell/bookings/range")  # Missing start and end
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


@patch('routes.library.library_db')
def test_library_booking_invalid_date_format(mock_library_db, client):
    """Test error handling for invalid date format"""
    response = client.get("/v1/library/powell/bookings/range?start=invalid-date&end=2025-03-08T23:59:59")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_server_error_handling(client):
    """Test graceful handling of server errors"""
    with patch('routes.gyms.gym_db.get_gym_by_slug') as mock_get_gym:
        # Simulate database error
        mock_get_gym.side_effect = Exception("Database connection error")
        response = client.get("/v1/gym/bfit")
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        # Ensure error doesn't expose implementation details
        assert "Database connection error" not in data["error"]


# ------------------ Input Validation Tests ------------------

def test_historical_data_with_invalid_period(client):
    """Test error handling for invalid period parameter"""
    response = client.get("/v1/historical/dining/bplate?period=invalid")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_date_format_validation(client):
    """Test validation of date formats"""
    response = client.get("/v1/historical/gym/bfit?date=2025-13-32")  # Invalid date
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


# ------------------ Integration Tests ------------------

def test_complete_facility_workflow(client):
    """Test a full workflow of getting all facilities and then details for each"""
    # First get all dining halls
    response_dining = client.get("/v1/dining")
    assert response_dining.status_code == 200
    dining_data = response_dining.get_json()
    
    # Get a list of slugs
    hall_slugs = [hall for hall in dining_data["data"]]
    
    # Then request details for each dining hall
    for hall_slug in hall_slugs:
        response_hall = client.get(f"/v1/dining/{hall_slug}")
        assert response_hall.status_code == 200
        hall_details = response_hall.get_json()
        assert hall_details["data"]["slug"] == hall_slug

def test_sorting_parameters(client):
    """Test sorting parameters"""
    response = client.get("/v1/gym?sort=occupancy&order=desc")
    assert response.status_code == 200
    # Verify ordering if applicable

@patch('routes.library.library_db')
def test_empty_results_handling(mock_library_db, client):
    """Test handling of endpoints that return empty results"""
    # Mock the database to return empty results
    mock_library_db.get_library_bookings_by_date_range.return_value = []
    response = client.get("/v1/library/powell/bookings/range?start=2025-03-08T00:00:00&end=2025-03-08T01:00:00")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) == 0  # Empty array, not error