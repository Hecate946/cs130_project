from dataclasses import dataclass
from datetime import datetime, timezone
from database.db import db

@dataclass
class Library(db.Model):
    """Represents a library and its metadata."""
    __tablename__ = "libraries"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(255), nullable=False, unique=True)
    slug: str = db.Column(db.String(255), nullable=False, unique=True)
    location: str = db.Column(db.String(255), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated: datetime = db.Column(db.DateTime, 
                                    default=lambda: datetime.now(timezone.utc),
                                    onupdate=lambda: datetime.now(timezone.utc))


@dataclass
class LibraryRoom(db.Model):
    """Represents a room within a library."""
    __tablename__ = "library_rooms"
    __table_args__ = (db.UniqueConstraint("library_id", "name", name="unique_room_per_library"),)

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id: int = db.Column(db.Integer, db.ForeignKey("libraries.id"), nullable=False)
    name: str = db.Column(db.String(255), nullable=False)
    capacity: int = db.Column(db.Integer, nullable=True)
    accessibility_features: str = db.Column(db.Text, nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated: datetime = db.Column(db.DateTime, 
                                    default=lambda: datetime.now(timezone.utc),
                                    onupdate=lambda: datetime.now(timezone.utc))
    bookings = db.relationship("LibraryBooking", back_populates="room", cascade="all, delete-orphan")


class LibraryBooking(db.Model):
    __tablename__ = "library_bookings"

    id: int = db.Column(db.Integer, primary_key=True)
    room_id: int = db.Column(db.Integer, db.ForeignKey("library_rooms.id", ondelete="CASCADE"))
    start_time: datetime = db.Column(db.DateTime, nullable=False)
    end_time: datetime = db.Column(db.DateTime, nullable=False)
    status: str = db.Column(db.String(20), nullable=False, default="available")
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated: datetime = db.Column(db.DateTime, 
                                    default=lambda: datetime.now(timezone.utc),
                                    onupdate=lambda: datetime.now(timezone.utc))
    room = db.relationship("LibraryRoom", back_populates="bookings")

    __table_args__ = (
        db.CheckConstraint("start_time < end_time", name="check_valid_timerange"),
        db.CheckConstraint("status in ('available', 'booked')", name="check_valid_status"),
        db.UniqueConstraint('room_id', 'start_time', 'end_time', name='unique_time_interval_per_room'),
    )