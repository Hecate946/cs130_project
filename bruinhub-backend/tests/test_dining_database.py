from flask import Flask
import pytest
from unittest.mock import patch, MagicMock
from database.dining import DiningDatabase
from models.dining import DiningHall, DiningCapacityHistory
from datetime import datetime, timezone


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        yield app


@pytest.fixture
def dining_db(app):
    return DiningDatabase()


@patch("database.dining.DiningHall.query")
def test_get_dining_hall_by_slug(mock_query, dining_db):
    """Test fetching dining hall by slug"""
    # Setup mock
    mock_hall = MagicMock()
    mock_hall.slug = "bplate"
    mock_query.filter_by.return_value.first.return_value = mock_hall

    # Call method
    hall = dining_db.get_dining_hall_by_slug("bplate")

    # Assertions
    assert hall == mock_hall
    mock_query.filter_by.assert_called_once_with(slug="bplate")


@patch("database.dining.DiningDatabase.get_dining_hall_by_slug")
@patch("database.dining.db.session")
def test_update_dining_hall_existing(mock_session, mock_get_hall, dining_db):
    """Test updating existing dining hall"""
    # Setup mocks
    mock_hall = MagicMock()
    mock_get_hall.return_value = mock_hall

    # Call method
    result = dining_db.update_dining_hall(
        slug="bplate",
        menu={"Breakfast": ["Eggs"]},
        hours_today={"open": "7:00 AM", "close": "9:00 PM"},
    )

    # Assertions
    assert result is True
    assert mock_hall.menu == {"Breakfast": ["Eggs"]}
    assert mock_hall.hours_today == {"open": "7:00 AM", "close": "9:00 PM"}
    mock_session.commit.assert_called_once()


@patch("database.dining.DiningDatabase.get_dining_hall_by_slug")
@patch("database.dining.DiningCapacityHistory")
@patch("database.dining.db.session")
def test_insert_dining_capacity(
    mock_session, mock_capacity_model, mock_get_hall, dining_db
):
    """Test inserting dining capacity record"""
    # Setup mocks
    mock_hall = MagicMock()
    mock_hall.id = 1
    mock_get_hall.return_value = mock_hall

    # Call method
    result = dining_db.insert_dining_capacity(slug="bplate", occupants=50, capacity=200)

    # Assertions
    assert result is True
    mock_capacity_model.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@patch("database.dining.DiningDatabase.get_dining_hall_by_slug")
@patch("database.dining.DiningDatabase.get_latest_dining_capacity")
def test_get_dining_hall_latest(mock_get_capacity, mock_get_hall, dining_db):
    """Test getting latest dining hall data"""
    # Setup mocks
    mock_hall = MagicMock()
    mock_hall.slug = "bplate"
    mock_hall.menu = {"Breakfast": ["Eggs"]}
    mock_hall.hours_today = {"open": "7:00 AM", "close": "9:00 PM"}
    mock_hall.last_updated = datetime.now(timezone.utc)
    mock_get_hall.return_value = mock_hall

    mock_capacity = MagicMock()
    mock_capacity.occupants = 50
    mock_capacity.capacity = 200
    mock_get_capacity.return_value = mock_capacity

    # Call method
    result = dining_db.get_dining_hall_latest("bplate")

    # Assertions
    assert result["slug"] == "bplate"
    assert result["menu"] == {"Breakfast": ["Eggs"]}
    assert result["hours_today"] == {"open": "7:00 AM", "close": "9:00 PM"}
    assert result["occupants"] == 50
    assert result["capacity"] == 200
