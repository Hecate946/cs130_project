from datetime import datetime
from typing import Dict, List
import json
from models.library import LibraryRoom, LibraryBooking
from database.manager import DatabaseManager
from config import LIBRARY_EID_TO_NAME_MAP
from sqlalchemy import text


def process_library_data(data: Dict, library_id: int, db: DatabaseManager):
    """Process raw JSON data from library API and store in database"""

    # Group slots by itemId (room)
    rooms_slots = {}
    for slot in data['slots']:
        room_id = slot['itemId']
        if room_id not in rooms_slots:
            rooms_slots[room_id] = []
        rooms_slots[room_id].append(slot)

    # Process each room
    for room_id, slots in rooms_slots.items():
        room_name = LIBRARY_EID_TO_NAME_MAP[room_id]
        # First, ensure room exists in database
        room = get_or_create_room(
            db=db,
            library_id=library_id,
            room_id=room_id,
            name=room_name  # You might want to get actual room names from somewhere
        )

        # Process all slots for this room
        process_room_slots(db, room.id, slots)


def get_or_create_room(db: DatabaseManager, library_id: int, room_id: int, name: str) -> LibraryRoom:
    """Get existing room or create new one"""
    room = db.session.execute(
        text("SELECT id FROM library_rooms WHERE library_id = :library_id AND name = :name"),
        {"library_id": library_id, "name": name}
    ).fetchone()

    if not room:
        room_id_value = db.session.execute(
            text("""
                INSERT INTO library_rooms (library_id, name, capacity)
                VALUES (:library_id, :name, :capacity)
                RETURNING id
            """),
            {"library_id": library_id, "name": name,
                "capacity": 1}  # Default capacity
        ).fetchone()[0]
    else:
        room_id_value = room[0]

    return LibraryRoom(id=room_id_value, library_id=library_id, name=name)


def process_room_slots(db: DatabaseManager, room_id: int, slots: List[Dict]):
    """Process and store all time slots for a room"""
    for slot in slots:
        # Convert strings to datetime objects
        start_time = datetime.strptime(slot['start'], '%Y-%m-%d %H: %M: %S')
        end_time = datetime.strptime(slot['end'], '%Y-%m-%d %H: %M: %S')

        # Determine status based on className
        status = 'booked' if slot.get(
            'className') == 's-lc-eq-checkout' else 'available'

        # Create or update booking
        db.session.execute(
            text("""
                INSERT INTO library_bookings (room_id, start_time, end_time, status)
                VALUES (:room_id, :start_time, :end_time, :status)
                ON CONFLICT (room_id, start_time, end_time)
                DO UPDATE SET status = EXCLUDED.status
            """),
            {"room_id": room_id, "start_time": start_time,
                "end_time": end_time, "status": status}
        )


def update_library_availability(library_id: int, json_file_path: str):
    """Update availability for a specific library from JSON file"""
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    db = DatabaseManager("your_database_url")
    process_library_data(data, library_id, db)
