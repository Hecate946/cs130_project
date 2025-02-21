import pytest
from datetime import datetime, timedelta
from flask import Flask
from models.library import db, Library, LibraryRoom, LibraryBooking
import requests
from scrapers.library import LibraryScrapers, get_date_range
from config import ALL_LIBRARY_URLS, LIBRARY_URL_CONFIG
from database.library import process_library_data
from config import LIBRARY_EID_TO_NAME_MAP

# Create a fixture that sets up a temporary in-memory database


@pytest.fixture
def app():
    app = Flask(__name__)
    # in-memory DB for tests
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app  # testing happens here
        db.session.remove()
        db.drop_all()


def test_create_library(app):
    with app.app_context():
        # Create a library and commit to the database
        lib = Library(name="Test Library", slug="test-library",
                      location="Test Location")
        db.session.add(lib)
        db.session.commit()

        # Query the library
        result = Library.query.filter_by(slug="test-library").first()
        assert result is not None
        assert result.name == "Test Library"
        assert result.location == "Test Location"


def test_create_library_room_and_booking(app):
    with app.app_context():
        # Create a library
        lib = Library(name="Room Library", slug="room-library",
                      location="Some Location")
        db.session.add(lib)
        db.session.commit()

        # Create a room associated with the library
        room = LibraryRoom(library_id=lib.id, name="Room A", capacity=15)
        db.session.add(room)
        db.session.commit()

        # Verify that the room is added
        result_room = LibraryRoom.query.filter_by(
            name="Room A", library_id=lib.id).first()
        assert result_room is not None
        assert result_room.capacity == 15

        # Create a booking for the room
        start_time = datetime(2025, 2, 20, 10, 0, 0)
        end_time = datetime(2025, 2, 20, 11, 0, 0)
        booking = LibraryBooking(
            room_id=result_room.id,
            start_time=start_time,
            end_time=end_time,
            status="available"
        )
        db.session.add(booking)
        db.session.commit()

        # Verify the booking
        result_booking = LibraryBooking.query.filter_by(
            room_id=result_room.id).first()
        assert result_booking is not None
        assert result_booking.status == "available"
        assert result_booking.start_time == start_time
        assert result_booking.end_time == end_time


def test_booking_time_constraint(app):
    with app.app_context():
        # Create a library and room
        lib = Library(name="Constraint Library",
                      slug="const-library", location="Constraint Location")
        db.session.add(lib)
        db.session.commit()

        room = LibraryRoom(library_id=lib.id, name="Room B", capacity=20)
        db.session.add(room)
        db.session.commit()

        # Attempt to create a booking where start_time is after end_time.
        start_time = datetime(2025, 2, 20, 12, 0, 0)
        end_time = datetime(2025, 2, 20, 11, 0, 0)
        booking = LibraryBooking(
            room_id=room.id,
            start_time=start_time,
            end_time=end_time,
            status="available"
        )
        db.session.add(booking)
        with pytest.raises(Exception):
            # Commit should raise an error because of the check constraint
            db.session.commit()


# Dummy response class to simulate requests.Response
class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.HTTPError("Dummy error occurred")

# A dummy post function to replace requests.post


def dummy_post(url, params=None, headers=None, data=None):
    # Check that dates are inserted
    # We assume the API returns a JSON with a "slots" key.
    dummy_data = {
        "slots": [
            {
                "itemId": "101",
                "start": "2025-02-20 10:00:00",
                "end": "2025-02-20 11:00:00",
                "className": "s-lc-eq-checkout",
            },
            {
                "itemId": "101",
                "start": "2025-02-20 11:00:00",
                "end": "2025-02-20 12:00:00",
                "className": "s-lc-eq-available",
            },
        ]
    }
    return DummyResponse(dummy_data)


def test_get_date_range():
    start, end = get_date_range(days=7)
    # Check that the output is in the expected format (YYYY-MM-DD)
    assert len(start) == 10
    assert len(end) == 10


def test_scrape_library_data(monkeypatch):
    # Override requests.post with our dummy_post
    monkeypatch.setattr(requests, "post", dummy_post)
    scraper = LibraryScrapers()
    results = scraper.scrape_library_data()
    print(results)
    # Check that we have results for each URL with valid config
    assert len(results) == len(LIBRARY_URL_CONFIG)

    # For each URL in ALL_LIBRARY_URLS that has valid config, we should have results.
    for url in ALL_LIBRARY_URLS:
        if url in LIBRARY_URL_CONFIG:
            assert url in results
            data = results[url]
            # Check that the dummy data is returned
            assert "slots" in data
            assert isinstance(data["slots"], list)
            first_slot = data["slots"][0]
            assert first_slot["itemId"] == "101"


# Dummy scraped JSON data for one library
dummy_scraped_data = {
    "slots": [
        {'start': '2025-02-20 12: 30: 00', 'end': '2025-02-20 13: 00: 00', 'itemId': 29694, 'checksum': 'f9b75d9297e178e58af35d37ca69b124', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-20 13: 00: 00', 'end': '2025-02-20 13: 30: 00', 'itemId': 29694, 'checksum': 'dd0f7b7a21151b0cce74970e78767378'
         },
        {'start': '2025-02-20 13: 30: 00', 'end': '2025-02-20 14: 00: 00', 'itemId': 29694, 'checksum': 'd7a7bce2b8e5b7627753f31e7a89e84d', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-20 14: 00: 00', 'end': '2025-02-20 14: 30: 00', 'itemId': 29694, 'checksum': '5b820bf1c62c49fbf785bb0db376646e', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-20 14: 30: 00', 'end': '2025-02-20 15: 00: 00', 'itemId': 29694, 'checksum': '66da7956dcd0eebf8296cb1a15a86bdf', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-20 15: 00: 00', 'end': '2025-02-20 15: 30: 00', 'itemId': 29694, 'checksum': 'b24dc28f0dd23d45a4eb235507170a1f', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-21 08: 30: 00', 'end': '2025-02-21 09: 00: 00', 'itemId': 29695, 'checksum': '72337dab1af73c65efe67fb151ea5294', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-21 09: 00: 00', 'end': '2025-02-21 09: 30: 00', 'itemId': 29695, 'checksum': 'c5a1d292d114dc570f9dbe3fc15b1e64', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-21 09: 30: 00', 'end': '2025-02-21 10: 00: 00', 'itemId': 29695, 'checksum': 'b645d48fea8dd45c3b533bed608dcd0f', 'className': 's-lc-eq-checkout'
         },
        {'start': '2025-02-21 10: 00: 00', 'end': '2025-02-21 10: 30: 00', 'itemId': 29695, 'checksum': '695c0a3a543f43ee4d8eea3ee4af2fee', 'className': 's-lc-eq-checkout'
         }
    ]
}

# Fixture to create a Flask app with an in-memory SQLite DB


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_process_library_data(app):
    with app.app_context():
        # Create a dummy Library record.
        lib = Library(name="Test Library", slug="test-library",
                      location="Test Location")
        db.session.add(lib)
        db.session.commit()

        # Call the function to process the dummy scraped data
        process_library_data(dummy_scraped_data, library_id=lib.id, db=db)

        # Query LibraryRoom table
        rooms = LibraryRoom.query.filter_by(library_id=lib.id).all()
        assert len(rooms) == 2

        for room in rooms:
            if room.id:  # we expect some identifier set by process_library_data
                pass

        # Query the LibraryBooking table to verify bookings got inserted.
        bookings = LibraryBooking.query.all()

        assert len(bookings) == 10

        # Check the first booking
        first_booking = bookings[0]
        assert first_booking.start_time == datetime.strptime(
            "2025-02-20 12:30:00", "%Y-%m-%d %H:%M:%S")
