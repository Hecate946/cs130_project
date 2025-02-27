import pytest
from datetime import datetime, timedelta
from flask import Flask
from models.library import db, Library, LibraryRoom, LibraryBooking
from database.library import LibraryDatabase
import requests
from scrapers.library import LibraryScrapers, get_date_range
from config.library import ALL_LIBRARY_URLS, LIBRARY_URL_CONFIG
from routes import api

# Create a fixture that sets up a temporary in-memory database


@pytest.fixture
def app():
    app = Flask(__name__)
    # in-memory DB for tests
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(api)
    print(app.url_map)
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

def test_process_library_data(app):
    with app.app_context():
        # Create a dummy Library record.
        lib = Library(name="Test Library", slug="test-library",
                      location="Test Location")
        db.session.add(lib)
        db.session.commit()

        library_db = LibraryDatabase()
        library_db.process_library_data(dummy_scraped_data, library_id=lib.id)

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


def test_get_library_details(app):
    with app.app_context():
        # Create a library record.
        lib = Library(name="Detail Library", slug="detail-library", location="Detail Location")
        db.session.add(lib)
        db.session.commit()

        # Instantiate the LibraryDatabase handler and retrieve details.
        library_db = LibraryDatabase()
        details = library_db.get_library_details("detail-library")
        assert details is not None
        assert details["name"] == "Detail Library"
        assert details["location"] == "Detail Location"

        
def test_process_library_data_multiple_rooms(app):
    with app.app_context():
        # Create a library record.
        lib = Library(name="Room Library", slug="room-library", location="Room Location")
        db.session.add(lib)
        db.session.commit()
        
        # Prepare dummy scraped data for two rooms.
        dummy_data = {
            "slots": [
                # Room 101 slots
                {'start': '2025-03-01 09:00:00', 'end': '2025-03-01 09:30:00',
                 'itemId': "101", 'checksum': 'checksum1', 'className': 's-lc-eq-checkout'},
                {'start': '2025-03-01 09:30:00', 'end': '2025-03-01 10:00:00',
                 'itemId': "101", 'checksum': 'checksum2', 'className': 's-lc-eq-available'},
                # Room 102 slots
                {'start': '2025-03-02 14:00:00', 'end': '2025-03-02 14:30:00',
                 'itemId': "102", 'checksum': 'checksum3', 'className': 's-lc-eq-checkout'},
                {'start': '2025-03-02 14:30:00', 'end': '2025-03-02 15:00:00',
                 'itemId': "102", 'checksum': 'checksum4', 'className': 's-lc-eq-checkout'},
            ]
        }
        
        library_db = LibraryDatabase()
        library_db.process_library_data(dummy_data, library_id=lib.id)
        
        # There should be two rooms based on the two unique itemIds.
        rooms = LibraryRoom.query.filter_by(library_id=lib.id).all()
        assert len(rooms) == 2
        
        # Verify each room has exactly 2 bookings.
        for room in rooms:
            bookings = LibraryBooking.query.filter_by(room_id=room.id).all()
            assert len(bookings) == 2

            
def test_get_library_bookings_by_date_range(app):
    with app.app_context():
        # Create a library record.
        lib = Library(name="Range Library", slug="range-library", location="Range Location")
        db.session.add(lib)
        db.session.commit()
        
        # Dummy data for one room with three slots, two of which fall on 2025-04-01.
        dummy_data = {
            "slots": [
                {'start': '2025-04-01 08:00:00', 'end': '2025-04-01 08:30:00',
                 'itemId': "201", 'checksum': 'cs1', 'className': 's-lc-eq-checkout'},
                {'start': '2025-04-01 09:00:00', 'end': '2025-04-01 09:30:00',
                 'itemId': "201", 'checksum': 'cs2', 'className': 's-lc-eq-checkout'},
                {'start': '2025-04-02 10:00:00', 'end': '2025-04-02 10:30:00',
                 'itemId': "201", 'checksum': 'cs3', 'className': 's-lc-eq-available'},
            ]
        }
        
        library_db = LibraryDatabase()
        library_db.process_library_data(dummy_data, library_id=lib.id)
        
        # Query bookings on 2025-04-01: expecting 2 bookings.
        start_range = datetime(2025, 4, 1, 0, 0, 0)
        end_range = datetime(2025, 4, 1, 23, 59, 59)
        bookings_in_range = library_db.get_library_bookings_by_date_range("range-library", start_range, end_range)
        assert bookings_in_range is not None
        assert len(bookings_in_range) == 2
        
        
def test_scrape_library_data(monkeypatch):
    # Test the scraping functionality via LibraryScrapers.
    def dummy_post(url, params=None, headers=None, data=None):
        dummy_data = {
            "slots": [
                {
                    "itemId": "101",
                    "start": "2025-02-20 10:00:00",
                    "end": "2025-02-20 11:00:00",
                    "className": "s-lc-eq-checkout",
                }
            ]
        }
        # A dummy response object.
        class DummyResponse:
            def __init__(self, json_data, status_code=200):
                self._json_data = json_data
                self.status_code = status_code

            def json(self):
                return self._json_data

            def raise_for_status(self):
                if self.status_code != 200:
                    raise Exception("HTTP error")
        return DummyResponse(dummy_data)
    
    monkeypatch.setattr(requests, "post", dummy_post)
    scraper = LibraryScrapers()
    results = scraper.scrape_library_data()
    
    # Verify that results exist for each configured URL.
    assert len(results) == len(LIBRARY_URL_CONFIG)
    # Verify the dummy data structure is preserved.
    for url, data in results.items():
        assert "slots" in data
        assert isinstance(data["slots"], list)
        assert data["slots"][0]["itemId"] == "101"


def test_get_library_details_route(app):
    with app.app_context():
        # Create a dummy library record.
        lib = Library(name="Powell Library", slug="powell", location="Powell Location")
        db.session.add(lib)
        db.session.commit()

        client = app.test_client()
        response = client.get("/v1/library/powell")
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert data["data"]["name"] == "Powell Library"
        assert data["data"]["location"] == "Powell Location"


def test_get_library_bookings_by_date_range_route(app):
    with app.app_context():
        # Create a dummy library record.
        lib = Library(name="Powell Library", slug="powell", location="Powell Location")
        db.session.add(lib)
        db.session.commit()
        
        # Create a room for the library.
        room = LibraryRoom(library_id=lib.id, name="Test Room")
        db.session.add(room)
        db.session.commit()
        
        # Create a booking that falls on 2025-02-20.
        start_t = datetime(2025, 2, 20, 12, 30, 0)
        end_t = datetime(2025, 2, 20, 13, 0, 0)
        booking = LibraryBooking(
            room_id=room.id,
            start_time=start_t,
            end_time=end_t,
            status="booked",
            created_at=start_t
        )
        db.session.add(booking)
        db.session.commit()
        
        client = app.test_client()
        # Valid query range that should include the booking.
        response = client.get("/v1/library/powell/bookings/range?start=2025-02-20T00:00:00&end=2025-02-20T23:59:59")
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert isinstance(data["data"], list)
        # There should be one booking.
        assert len(data["data"]) == 1
        # Verify the booking times match.
        b = data["data"][0]
        assert b["start_time"] == start_t.isoformat()
        assert b["end_time"] == end_t.isoformat()


def test_get_library_rooms_route(app):
    with app.app_context():
        # Create a dummy library record.
        lib = Library(name="Powell Library", slug="powell", location="Powell Location")
        db.session.add(lib)
        db.session.commit()
        
        # Create two rooms with bookings.
        for room_name, start_hour in [("Room A", 10), ("Room B", 14)]:
            room = LibraryRoom(library_id=lib.id, name=room_name)
            db.session.add(room)
            db.session.commit()
            # Create a booking for each room.
            start_time = datetime(2025, 3, 1, start_hour, 0, 0)
            end_time = datetime(2025, 3, 1, start_hour, 30, 0)
            booking = LibraryBooking(
                room_id=room.id,
                start_time=start_time,
                end_time=end_time,
                status="booked",
                created_at=start_time
            )
            db.session.add(booking)
            db.session.commit()
        
        client = app.test_client()
        response = client.get("/v1/library/powell/rooms")
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        # There should be two rooms.
        assert len(data["data"]) == 2
        # Check that each room entry has a bookings list.
        for room in data["data"]:
            assert "bookings" in room
            # Each room has at least one booking.
            assert len(room["bookings"]) >= 1


def test_missing_date_params_in_range_route(app):
    with app.app_context():
        client = app.test_client()
        # Omit the 'end' parameter.
        response = client.get("/v1/library/powell/bookings/range?start=2025-02-20T00:00:00")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Both 'start' and 'end' query parameters are required" in data["error"]


def test_invalid_date_format_route(app):
    with app.app_context():
        # Create a dummy library record.
        lib = Library(name="Invalid Date Library", slug="invalid-date", location="Nowhere")
        db.session.add(lib)
        db.session.commit()

        client = app.test_client()
        response = client.get("/v1/library/invalid-date/bookings/range?start=invalid-date&end=2025-02-20T23:59:59")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Invalid date format" in data["error"]


def test_missing_start_and_both_dates(app):
    with app.app_context():
        lib = Library(name="Missing Dates Library", slug="missing-dates", location="Nowhere")
        db.session.add(lib)
        db.session.commit()

        client = app.test_client()
        # Missing start and end.
        response = client.get("/v1/library/missing-dates/bookings/range")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Both 'start' and 'end' query parameters are required" in data["error"]

        # Missing start parameter.
        response = client.get("/v1/library/missing-dates/bookings/range?end=2025-02-20T23:59:59")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Both 'start' and 'end' query parameters are required" in data["error"]


def test_nonexistent_library_detail_route(app):
    with app.app_context():
        client = app.test_client()
        # Using a slug that has no record.
        response = client.get("/v1/library/nonexistent")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


def test_method_not_allowed_on_library_route(app):
    with app.app_context():
        lib = Library(name="Method Test Library", slug="method-test", location="Nowhere")
        db.session.add(lib)
        db.session.commit()

        client = app.test_client()
        # Sending POST instead of GET should return 405.
        response = client.post("/v1/library/method-test")
        assert response.status_code == 405


def test_scrape_library_data_error(monkeypatch):
    # Override requests.post to simulate an HTTP error
    def dummy_post_error(url, params=None, headers=None, data=None):
        class DummyResponse:
            def __init__(self, json_data, status_code=500):
                self._json_data = json_data
                self.status_code = status_code

            def json(self):
                return self._json_data

            def raise_for_status(self):
                raise requests.exceptions.HTTPError("Simulated error")

        return DummyResponse({"error": "Simulated error"}, status_code=500)

    monkeypatch.setattr(requests, "post", dummy_post_error)
    
    scraper = LibraryScrapers()
    results = scraper.scrape_library_data()
    
    assert results == dict()


def test_process_library_data_idempotent(app):
    """
    Test that processing the same scraped data twice does not duplicate bookings.
    """
    with app.app_context():
        lib = Library(name="Idempotent Library", slug="idempotent", location="Test Location")
        db.session.add(lib)
        db.session.commit()

        library_db = LibraryDatabase()
        # Process data twice
        library_db.process_library_data(dummy_scraped_data, library_id=lib.id)
        library_db.process_library_data(dummy_scraped_data, library_id=lib.id)

        rooms = LibraryRoom.query.filter_by(library_id=lib.id).all()
        # Expect two rooms
        assert len(rooms) == 2

        bookings = LibraryBooking.query.all()
        # Even though we processed twice, total bookings remain 10 (due to upsert behavior)
        assert len(bookings) == 10

def test_get_library_rooms_no_bookings(app):
    """
    Test get_library_rooms when rooms exist but have no bookings.
    """
    with app.app_context():
        lib = Library(name="Empty Rooms Library", slug="empty-rooms", location="Test Location")
        db.session.add(lib)
        db.session.commit()

        # Manually create rooms without any bookings.
        room1 = LibraryRoom(library_id=lib.id, name="Room X", capacity=10)
        room2 = LibraryRoom(library_id=lib.id, name="Room Y", capacity=20)
        db.session.add_all([room1, room2])
        db.session.commit()

        client = app.test_client()
        response = client.get("/v1/library/empty-rooms/rooms")
        assert response.status_code == 200
        data = response.get_json()
        # There should be two rooms, each with an empty 'bookings' list.
        assert len(data["data"]) == 2
        for room in data["data"]:
            assert "bookings" in room
            assert isinstance(room["bookings"], list)
            assert len(room["bookings"]) == 0

def test_overlapping_booking_update(app):
    """
    Test that processing library data with overlapping time slots updates an existing booking
    instead of creating duplicates.
    """
    with app.app_context():
        lib = Library(name="Overlap Library", slug="overlap", location="Test Location")
        db.session.add(lib)
        db.session.commit()

        # Create dummy data with a booking slot, then a modified version.
        dummy_data_original = {
            "slots": [
                {'start': '2025-05-01 09:00:00', 'end': '2025-05-01 09:30:00',
                 'itemId': "500", 'checksum': 'orig1', 'className': 's-lc-eq-checkout'},
            ]
        }
        dummy_data_updated = {
            "slots": [
                {'start': '2025-05-01 09:00:00', 'end': '2025-05-01 09:30:00',
                 'itemId': "500", 'checksum': 'upd1', 'className': 's-lc-eq-available'},
            ]
        }
        library_db = LibraryDatabase()
        # Process original data then updated (overlapping same time slot)
        library_db.process_library_data(dummy_data_original, library_id=lib.id)
        library_db.process_library_data(dummy_data_updated, library_id=lib.id)

        # Check that there's only one booking for room with itemId "500"
        room = LibraryRoom.query.filter_by(library_id=lib.id, name="Room 500").first()
        assert room is not None
        bookings = LibraryBooking.query.filter_by(room_id=room.id).all()
        assert len(bookings) == 1
        # Status should reflect updated value ("available")
        assert bookings[0].status == "available"

def test_get_library_bookings_by_date_range_no_results(app):
    """
    Test that querying for bookings in a date range with no bookings returns 404 or error message.
    """
    with app.app_context():
        lib = Library(name="No Results Library", slug="noresults", location="Test Location")
        db.session.add(lib)
        db.session.commit()

        library_db = LibraryDatabase()
        # Process dummy data that does not include bookings for 2025-06-01.
        dummy_data = {
            "slots": [
                {'start': '2025-05-01 08:00:00', 'end': '2025-05-01 08:30:00',
                 'itemId': "300", 'checksum': 'cs1', 'className': 's-lc-eq-checkout'},
            ]
        }
        library_db.process_library_data(dummy_data, library_id=lib.id)

        start_range = datetime(2025, 6, 1, 0, 0, 0)
        end_range = datetime(2025, 6, 1, 23, 59, 59)
        bookings_in_range = library_db.get_library_bookings_by_date_range("noresults", start_range, end_range)

        assert bookings_in_range == []
