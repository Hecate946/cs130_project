import logging
from datetime import datetime, timezone
from typing import Optional, List
from models.rec import db, RecUser, ReservationTask, SessionTask, TaskStatus

logger = logging.getLogger(__name__)


class RecDatabase:
    """Handles recreation-related database operations."""

    def __init__(self):
        logger.info("Initialized RecDatabase")

    def get_active_users(self) -> List[RecUser]:
        """Fetch all users with active session tasks."""
        return (
            RecUser.query.join(SessionTask)
            .filter(SessionTask.status == TaskStatus.running)
            .all()
        )

    def get_user_by_party_id(self, party_id: str) -> Optional[RecUser]:
        """Fetch a user by their Party ID."""
        return RecUser.query.filter_by(party_id=party_id).first()

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

    def get_pending_reservation_tasks(self) -> List[ReservationTask]:
        """Retrieve all scheduled reservation tasks that haven't been completed."""
        return ReservationTask.query.filter(
            ReservationTask.status == TaskStatus.running
        ).all()

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
