import enum
from datetime import datetime, timezone
from database.db import db


class TaskStatus(enum.Enum):
    running = "running"
    failed = "failed"
    completed = "completed"
    cancelled = "cancelled"


class RecUser(db.Model):
    """Stores user information and session cookies to maintain login state."""
    __tablename__ = "recreation_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    party_id = db.Column(db.String(36), unique=True, nullable=False)  # UUID for the user
    aspnet_cookie = db.Column(db.String(2048), nullable=False)         # Authentication cookie
    last_login = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    reservations = db.relationship("Reservation", backref="user", lazy=True, cascade="all, delete-orphan")
    reservation_tasks = db.relationship("ReservationTask", backref="user", lazy=True, cascade="all, delete-orphan")
    session_task = db.relationship("SessionTask", backref="user", lazy=True, cascade="all, delete-orphan")


class Reservation(db.Model):
    """Tracks user reservations for recreation facilities."""
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("recreation_users.id"), nullable=False)
    
    # Store facility id as a string; facility IDs are hardcoded in config.
    facility_id = db.Column(db.String(36), nullable=False)
    
    # Store court slot details returned from the booking API.
    court_slot = db.Column(db.String(36), nullable=False)  # Unique court slot id
    court_name = db.Column(db.String(36), nullable=False)    # e.g., "SYCA - 1"
    
    # Timing information for the reservation.
    reservation_time = db.Column(db.DateTime, nullable=False)  # When the reservation was made
    start_time = db.Column(db.DateTime, nullable=False)        # When the reservation begins
    end_time = db.Column(db.DateTime, nullable=False)          # When the reservation ends

    participant_id = db.Column(db.String(36), nullable=False)  # Reservation identifier from UCLA Rec

    canceled = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)


class ReservationTask(db.Model):
    """Tracks scheduled tasks for making future reservations."""
    __tablename__ = "reservation_tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("recreation_users.id"), nullable=False)
    
    # Store facility id as a string; facility IDs come from your config.
    facility_id = db.Column(db.String(36), nullable=False)
    
    # Store the court slot info dynamically fetched from the booking API.
    court_slot = db.Column(db.String(36), nullable=False)
    
    # The desired reservation date + time.
    desired_date = db.Column(db.Date, nullable=False)
    desired_time = db.Column(db.Time, nullable=False)
    
    # When the system should attempt to reserve the slot.
    schedule_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.running) 
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)


class SessionTask(db.Model):
    """Maintains tasks for keeping users logged in by refreshing cookies."""
    __tablename__ = "session_tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("recreation_users.id"), nullable=False)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.running) 
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
