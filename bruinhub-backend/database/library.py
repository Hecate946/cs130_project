from datetime import datetime
from typing import Dict, List, Optional
import logging
from sqlalchemy import text

from models.library import db, Library, LibraryRoom, LibraryBooking
from database.manager import DatabaseManager
from config import LIBRARY_EID_TO_NAME_MAP

logger = logging.getLogger(__name__)

class LibraryDatabase:
    def __init__(self):
        logger.info("Initialized LibraryDatabase")

    def get_library_details(self, slug: str) -> Optional[Dict]:
        """Return a dictionary of library details given its slug."""
        library = Library.query.filter_by(slug=slug).first()
        if library:
            return {
                "id": library.id,
                "name": library.name,
                "slug": library.slug,
                "location": library.location,
                "created_at": library.created_at.isoformat() if library.created_at else None
            }
        return None
    
    def get_library_id_by_name(self, name: str) -> Optional[int]:
        """Return the ID of a library given its name."""
        library = Library.query.filter_by(name=name).first()
        if library:
            return library.id
        return None
    
    def get_library_bookings(self, slug: str) -> Optional[List[Dict]]:
        """Return an array of booking dictionaries for the library identified by slug."""
        library = Library.query.filter_by(slug=slug).first()
        if not library:
            return None

        bookings = (LibraryBooking.query
                    .join(LibraryRoom, LibraryRoom.id == LibraryBooking.room_id)
                    .filter(LibraryRoom.library_id == library.id)
                    .all())
        results = []
        for booking in bookings:
            results.append({
                "id": booking.id,
                "room_id": booking.room_id,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "status": booking.status,
                "created_at": booking.created_at.isoformat() if booking.created_at else None
            })
        return results

    def get_library_rooms(self, slug: str) -> Optional[List[Dict]]:
        """Return an array of room dictionaries (with booking info) for the library."""
        library = Library.query.filter_by(slug=slug).first()
        if not library:
            return None

        rooms = LibraryRoom.query.filter_by(library_id=library.id).all()
        results = []
        for room in rooms:
            room_data = {
                "id": room.id,
                "name": room.name,
                "capacity": room.capacity,
                "accessibility_features": room.accessibility_features,
                "last_updated": room.last_updated.isoformat() if room.last_updated else None,
                "created_at": room.created_at.isoformat() if room.created_at else None,
                "bookings": []
            }
            bookings = LibraryBooking.query.filter_by(room_id=room.id).all()
            for booking in bookings:
                room_data["bookings"].append({
                    "id": booking.id,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat(),
                    "status": booking.status,
                    "created_at": booking.created_at.isoformat() if booking.created_at else None
                })
            results.append(room_data)
        return results

    def get_library_bookings_by_date_range(self, slug: str, start_date: datetime, end_date: datetime) -> Optional[List[Dict]]:
        """
        Return an array of bookings for a library that have start_time and end_time within the specified range.
        """
        library = Library.query.filter_by(slug=slug).first()
        if not library:
            return None

        bookings = (LibraryBooking.query
                    .join(LibraryRoom, LibraryRoom.id == LibraryBooking.room_id)
                    .filter(LibraryRoom.library_id == library.id)
                    .filter(LibraryBooking.start_time >= start_date)
                    .filter(LibraryBooking.end_time <= end_date)
                    .all())
        results = []
        for booking in bookings:
            results.append({
                "id": booking.id,
                "room_id": booking.room_id,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "status": booking.status,
                "created_at": booking.created_at.isoformat() if booking.created_at else None
            })
        return results

    def process_library_data(self, data: Dict, library_id: int):
        """
        Process raw JSON data from a library API and store it in the database.
        Groups slots by room, ensures the room exists, then processes each slot.
        """
        # Group slots by itemId (room)
        rooms_slots = {}
        for slot in data["slots"]:
            room_id = slot["itemId"]
            if room_id not in rooms_slots:
                rooms_slots[room_id] = []
            rooms_slots[room_id].append(slot)

        # Process each room
        for room_id, slots in rooms_slots.items():
            room_name = LIBRARY_EID_TO_NAME_MAP.get(room_id, f"Room {room_id}")
            # Ensure room exists in database
            logger.info(f"Processing room {room_name} for library ID {library_id}")
            room = self._get_or_create_room(library_id, room_id, room_name)
            if not room:
                logger.error(f"Error creating room {room_name} for library ID {library_id}")
                continue
            # Process all slots for this room
            logger.info(f"Processing {len(slots)} slots for room {room_name}")
            self._process_room_slots(room.id, slots)
        
            

    def _get_or_create_room(self, library_id: int, room_id: int, name: str) -> LibraryRoom:
        """Get an existing room or create a new one using SQLAlchemy ORM."""
        room = LibraryRoom.query.filter_by(library_id=library_id, name=name).first()
        
        if not room:
            room = LibraryRoom(
                library_id=library_id,
                name=name,
                capacity=1  # Default capacity
            )
            db.session.add(room)
            db.session.commit()
        
        return room

    def _process_room_slots(self, room_id: int, slots: List[Dict]):
        """Process and store all time slots for a room using SQLAlchemy ORM."""
        for slot in slots:
            # Clean the time strings by replacing ": " with ":"
            start = slot["start"].replace(": ", ":")
            end = slot["end"].replace(": ", ":")
            
            # Convert strings to datetime objects
            start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            status = "booked" if slot.get("className") == "s-lc-eq-checkout" else "available"

            # Try to find existing booking
            booking = LibraryBooking.query.filter_by(
                room_id=room_id,
                start_time=start_time,
                end_time=end_time
            ).first()

            if booking:
                booking.status = status
            else:
                booking = LibraryBooking(
                    room_id=room_id,
                    start_time=start_time,
                    end_time=end_time,
                    status=status
                )
                db.session.add(booking)
        
        db.session.commit()
        logger.info(f"Processed {len(slots)} slots for room ID {room_id}")

