import unittest
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime, date, time, timezone, timedelta

from models.rec import RecUser, ReservationTask, TaskStatus, Reservation
from database.rec import RecDatabase
from tasks.rec_tasks import attempt_reservations
from config.rec import REC_FACILITIES
from app import app


class TestReservation(unittest.TestCase):
    def setUp(self):
        # Set up test user and reservation data
        self.test_user = MagicMock(spec=RecUser)
        self.test_user.id = 1
        self.test_user.party_id = "test-party-id"
        self.test_user.aspnet_cookie = "test-cookie"
        
        # Create test reservation task
        self.test_reservation_task = MagicMock(spec=ReservationTask)
        self.test_reservation_task.id = 1
        self.test_reservation_task.user_id = self.test_user.id
        self.test_reservation_task.facility_id = REC_FACILITIES[0]['id']  # First facility in config
        self.test_reservation_task.court_slot = "test-court-slot-id"
        self.test_reservation_task.desired_date = date(2025, 3, 15)
        self.test_reservation_task.desired_time = time(14, 0)
        self.test_reservation_task.schedule_at = datetime(2025, 3, 15, 7, 0, tzinfo=timezone.utc)
        self.test_reservation_task.status = TaskStatus.running
        
        # Create application context for tests
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        # Remove application context after test
        self.app_context.pop()

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.post')
    def test_successful_reservation(self, mock_post, mock_rec_db):
        """Test that a court reservation is successfully processed."""
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task]
        mock_rec_db.get_user_by_party_id.return_value = self.test_user
        mock_rec_db.mark_reservation_task_completed.return_value = True
        
        # Mock the reservation response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Reservation successfully placed"
        
        mock_post.return_value = mock_response
        
        # Execute the function
        attempt_reservations()
        
        # Assert function behavior
        mock_rec_db.get_pending_reservation_tasks.assert_called_once()
        mock_rec_db.get_user_by_party_id.assert_called_once_with(self.test_user.id)
        mock_rec_db.mark_reservation_task_completed.assert_called_once_with(self.test_reservation_task.id)
        mock_post.assert_called_once()

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.post')
    def test_failed_reservation(self, mock_post, mock_rec_db):
        """Test handling of failed court reservation."""
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task]
        mock_rec_db.get_user_by_party_id.return_value = self.test_user
        
        # Mock the reservation response with failure
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Court is already booked"
        
        mock_post.return_value = mock_response
        
        # Execute the function
        attempt_reservations()
        
        # Assert behavior
        mock_rec_db.get_pending_reservation_tasks.assert_called_once()
        mock_rec_db.get_user_by_party_id.assert_called_once_with(self.test_user.id)
        mock_rec_db.mark_reservation_task_completed.assert_not_called()
        mock_post.assert_called_once()

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.post')
    def test_request_exception(self, mock_post, mock_rec_db):
        """Test handling of request exceptions during reservation attempt."""
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task]
        mock_rec_db.get_user_by_party_id.return_value = self.test_user
        
        # Mock request.post to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException("Test error")
        
        # Execute the function (should not raise an exception)
        attempt_reservations()
        
        # Assert behavior when exception occurs
        mock_rec_db.get_pending_reservation_tasks.assert_called_once()
        mock_rec_db.get_user_by_party_id.assert_called_once_with(self.test_user.id)
        mock_rec_db.mark_reservation_task_completed.assert_not_called()

    @patch('tasks.rec_tasks.rec_db')
    def test_no_user_for_task(self, mock_rec_db):
        """Test handling of tasks with no associated user."""
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task]
        mock_rec_db.get_user_by_party_id.return_value = None  # No user found
        
        # Execute the function (should not raise an exception)
        attempt_reservations()
        
        # Assert behavior
        mock_rec_db.get_pending_reservation_tasks.assert_called_once()
        mock_rec_db.get_user_by_party_id.assert_called_once_with(self.test_user.id)
        mock_rec_db.mark_reservation_task_completed.assert_not_called()

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.post')
    def test_multiple_pending_reservations(self, mock_post, mock_rec_db):
        """Test processing multiple pending reservation tasks."""
        # Create a second test task
        second_task = MagicMock(spec=ReservationTask)
        second_task.id = 2
        second_task.user_id = self.test_user.id
        second_task.facility_id = REC_FACILITIES[1]['id']  # Second facility
        second_task.court_slot = "second-court-slot-id"
        second_task.desired_date = date(2025, 3, 16)
        second_task.desired_time = time(15, 0)
        second_task.schedule_at = datetime(2025, 3, 16, 7, 0, tzinfo=timezone.utc)
        second_task.status = TaskStatus.running
        
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task, second_task]
        mock_rec_db.get_user_by_party_id.return_value = self.test_user
        
        # First call succeeds, second call fails
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.text = "Reservation successfully placed"
        
        second_response = MagicMock()
        second_response.status_code = 400
        second_response.text = "Court is already booked"
        
        mock_post.side_effect = [first_response, second_response]
        
        # Execute the function
        attempt_reservations()
        
        # Assert behavior
        self.assertEqual(mock_rec_db.get_user_by_party_id.call_count, 2)
        self.assertEqual(mock_post.call_count, 2)
        mock_rec_db.mark_reservation_task_completed.assert_called_once_with(self.test_reservation_task.id)

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.post')
    def test_reservation_with_dynamic_parameters(self, mock_post, mock_rec_db):
        """Test reservation with dynamically filled parameters (aId, tsId, tsiId)."""
        # Set up mock responses and database
        mock_rec_db.get_pending_reservation_tasks.return_value = [self.test_reservation_task]
        mock_rec_db.get_user_by_party_id.return_value = self.test_user
        mock_rec_db.mark_reservation_task_completed.return_value = True
        
        # Mock the reservation response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Reservation successfully placed"
        
        mock_post.return_value = mock_response
        
        # Execute the function
        attempt_reservations()
        
        # Check that payload contains expected values
        call_args = mock_post.call_args
        self.assertIn('data', call_args[1])
        payload = call_args[1]['data']
        
        self.assertEqual(payload['bId'], self.test_reservation_task.facility_id)
        self.assertEqual(payload['fId'], self.test_reservation_task.court_slot)
        self.assertEqual(payload['y'], self.test_reservation_task.desired_date.year)
        self.assertEqual(payload['m'], self.test_reservation_task.desired_date.month)
        self.assertEqual(payload['d'], self.test_reservation_task.desired_date.day)


if __name__ == '__main__':
    unittest.main()