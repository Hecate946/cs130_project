from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


@dataclass
class Library(db.Model):
    """Represents a library and its metadata."""
    __tablename__ = "libraries"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(255), nullable=False)
    slug: str = db.Column(db.String(255), unique=True, nullable=False)
    created_at: datetime = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))
    location: str = db.Column(db.String(255), nullable=True)


@dataclass
class LibraryRoom(db.Model):
    """Represents a room within a library."""
    __tablename__ = "library_rooms"
    __table_args__ = (db.UniqueConstraint(
        'name', 'library_id', name='unique_room_per_library'),)

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    library_id: int = db.Column(
        db.Integer, db.ForeignKey("libraries.id"), nullable=False)
    name: str = db.Column(db.String(255), nullable=False)
    capacity: int = db.Column(db.Integer, nullable=True)
    accessibility_features: Optional[str] = db.Column(db.Text, nullable=True)
    last_updated: datetime = db.Column(db.DateTime, default=datetime.now(
        timezone.utc), onupdate=datetime.now(timezone.utc))
    created_at: datetime = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))

    bookings = db.relationship(
        "LibraryBooking", back_populates="room", cascade="all, delete-orphan")


class LibraryBooking(db.Model):
    __tablename__ = 'library_bookings'

    id: int = db.Column(db.Integer, primary_key=True)
    room_id: int = db.Column(db.Integer, db.ForeignKey(
        'library_rooms.id', ondelete='CASCADE'))
    start_time: datetime = db.Column(db.DateTime, nullable=False)
    end_time: datetime = db.Column(db.DateTime, nullable=False)
    status: str = db.Column(db.String(20), default='available', nullable=False)
    created_at: datetime = db.Column(
        db.DateTime, default=datetime.now(timezone.utc))

    # Relationship
    room = db.relationship("LibraryRoom", back_populates="bookings")

    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            status.in_(['available', 'booked']),
            name='check_valid_status'
        ),
        db.CheckConstraint(
            'start_time < end_time',
            name='check_valid_timerange'
        ),
        db.UniqueConstraint('room_id', 'start_time', 'end_time',
                            name='unique_time_interval_per_room'),
    )
