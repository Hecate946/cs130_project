import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from models.rec import db, RecUser, ReservationTask, SessionTask, TaskStatus, Reservation

logger = logging.getLogger(__name__)

class RecDatabase:
    """Handles recreation-related database operations."""

    def __init__(self):
        logger.info("Initialized RecDatabase")

    def get_active_users(self) -> List[RecUser]:
        """Fetch all users with active session tasks."""
        return RecUser.query.join(SessionTask).filter(SessionTask.status == TaskStatus.running).all()

    def get_user_by_party_id(self, party_id: str) -> Optional[RecUser]:
        """Fetch a user by their Party ID."""
        return RecUser.query.filter_by(party_id=party_id).first()
    
    def create_or_update_user(self, party_id: str, aspnet_cookie: str):
            """
            Creates a new user or updates an existing user's session cookie.
            """
            user = self.get_user_by_party_id(party_id)
            if user:
                user.aspnet_cookie = aspnet_cookie
                user.last_login = datetime.now(timezone.utc)
            else:
                user = RecUser(
                    party_id=party_id,
                    aspnet_cookie=aspnet_cookie,
                    last_login=datetime.now(timezone.utc)
                )
                db.session.add(user)

            db.session.commit()
            return user
    
    def create_or_update_session_task(self, user_id: int, status: TaskStatus):
        """
        Creates or updates a session task for the user.
        If a session task exists, updates its status.
        """
        session_task = SessionTask.query.filter_by(user_id=user_id).first()
        if session_task:
            session_task.status = status
            session_task.last_updated = datetime.now(timezone.utc)
        else:
            session_task = SessionTask(
                user_id=user_id,
                status=status,
                created_at=datetime.now(timezone.utc),
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(session_task)

        db.session.commit()
        return session_task

    def update_session_cookie(self, party_id: str, new_cookie: str) -> bool:
        """Update the user's session cookie."""
        user = self.get_user_by_party_id(party_id)
        if not user:
            logger.error(f"User with Party ID {party_id} not found.")
            return False

        user.aspnet_cookie = new_cookie
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        logger.info(f"Updated session cookie for Party ID {party_id}")
        return True
    
    def store_reservation(self, user_id: int, facility_id: str, court_slot: str, court_name: str, start_time: str, end_time: str, participant_id: str):
        """
        Stores a new reservation in the database.
        """
        reservation = Reservation(
            user_id=user_id,
            facility_id=facility_id,
            court_slot=court_slot,
            court_name=court_name,
            reservation_time=datetime.now(timezone.utc),
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            participant_id=participant_id,
            canceled=False
        )
        db.session.add(reservation)
        db.session.commit()
    
    def schedule_reservation_task(self, user_id: int, facility_id: str, court_slot: str, desired_date: datetime, desired_time: datetime):
            """Schedules a reservation task exactly 3 days before the desired date."""
            schedule_at = datetime.combine(desired_date, desired_time) - timedelta(days=3)

            task = ReservationTask(
                user_id=user_id,
                facility_id=facility_id,
                court_slot=court_slot,
                desired_date=desired_date,
                desired_time=desired_time,
                schedule_at=schedule_at,
                status=TaskStatus.running,
                created_at=datetime.now(timezone.utc)
            )

            db.session.add(task)
            db.session.commit()

    def get_pending_reservation_tasks(self) -> List[ReservationTask]:
        """Retrieve all scheduled reservation tasks that haven't been completed."""
        return ReservationTask.query.filter(ReservationTask.status == TaskStatus.running).all()

    def mark_reservation_task_completed(self, task_id: int) -> bool:
        """Mark a reservation task as completed."""
        task = ReservationTask.query.filter_by(id=task_id).first()
        if not task:
            logger.error(f"Reservation task {task_id} not found.")
            return False

        task.status = TaskStatus.completed
        db.session.commit()
        logger.info(f"Marked reservation task {task_id} as completed.")
        return True

    def mark_session_invalid(self, user_id: int) -> bool:
        """Mark a user's session as invalid (i.e., requires re-authentication)."""
        session_task = SessionTask.query.filter_by(user_id=user_id).first()
        if not session_task:
            logger.error(f"Session task for User ID {user_id} not found.")
            return False

        session_task.status = TaskStatus.failed
        db.session.commit()
        logger.info(f"Marked session task for User ID {user_id} as failed.")
        return True

    def get_user_reservations(self, user_id: int):
        """
        Fetches all non-canceled reservations for a user.
        """
        return Reservation.query.filter_by(user_id=user_id, canceled=False).all()