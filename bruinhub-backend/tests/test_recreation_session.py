import unittest
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime, timezone

from models.rec import RecUser, SessionTask, TaskStatus
from database.rec import RecDatabase
from tasks.rec_tasks import check_and_refresh_sessions, setup_rec_tasks
from config.rec import AUTH_CHECK_URL, VERIFY_URL
from app import app  # Import the Flask app


class TestRecreationSession(unittest.TestCase):
    def setUp(self):
        # Set up test user and session data
        self.test_user = MagicMock(spec=RecUser)
        self.test_user.id = 1
        self.test_user.party_id = "test-party-id"
        self.test_user.aspnet_cookie = "test-cookie"
        
        self.test_session_task = MagicMock(spec=SessionTask)
        self.test_session_task.id = 1
        self.test_session_task.user_id = 1
        self.test_session_task.status = TaskStatus.running
        
        # Create application context for tests
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        # Remove application context after test
        self.app_context.pop()

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.get')
    def test_successful_authentication_check(self, mock_get, mock_rec_db):
        """Test that an authenticated session is properly verified and maintained."""
        # Set up mock responses and database
        mock_rec_db.get_active_users.return_value = [self.test_user]
        
        # Mock the auth check response
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"IsAuthenticated": True}
        
        # Mock the verify response
        verify_response = MagicMock()
        verify_response.status_code = 200
        
        # Configure mock to return different responses for different URLs
        def get_side_effect(url, **kwargs):
            if url == AUTH_CHECK_URL:
                return auth_response
            elif url == VERIFY_URL:
                return verify_response
            return MagicMock(status_code=404)
            
        mock_get.side_effect = get_side_effect
        
        # Execute the function
        check_and_refresh_sessions()
        
        # Assert function behavior
        mock_rec_db.get_active_users.assert_called_once()
        self.assertEqual(mock_get.call_count, 2)  # Should call both auth and verify endpoints

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.get')
    def test_cookie_refresh(self, mock_get, mock_rec_db):
        """Test that new cookies are properly stored when received."""
        # Set up mock responses and database
        mock_rec_db.get_active_users.return_value = [self.test_user]
        mock_rec_db.update_session_cookie.return_value = True
        
        # Mock the auth check response with a new cookie
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"IsAuthenticated": True}
        auth_response.cookies = MagicMock()
        auth_response.cookies.get.return_value = "new-test-cookie"
        
        # Mock the verify response
        verify_response = MagicMock()
        verify_response.status_code = 200
        
        # Configure mock to return different responses
        def get_side_effect(url, **kwargs):
            if url == AUTH_CHECK_URL:
                return auth_response
            elif url == VERIFY_URL:
                return verify_response
            return MagicMock(status_code=404)
            
        mock_get.side_effect = get_side_effect
        
        # Execute the function
        check_and_refresh_sessions()
        
        # Assert that cookie was updated
        mock_rec_db.update_session_cookie.assert_called_once_with(
            self.test_user.party_id, "new-test-cookie"
        )

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.get')
    def test_unauthenticated_session(self, mock_get, mock_rec_db):
        """Test that an unauthenticated session is properly marked as invalid."""
        # Set up mock responses and database
        mock_rec_db.get_active_users.return_value = [self.test_user]
        mock_rec_db.mark_session_invalid.return_value = True
        
        # Mock the auth check response indicating user is not authenticated
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"IsAuthenticated": False}
        
        mock_get.return_value = auth_response
        
        # Execute the function
        check_and_refresh_sessions()
        
        # Assert that session was marked invalid
        mock_rec_db.mark_session_invalid.assert_called_once_with(self.test_user.id)

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.get')
    def test_verify_response_failure(self, mock_get, mock_rec_db):
        """Test that a failed verification response marks session as invalid."""
        # Set up mock responses and database
        mock_rec_db.get_active_users.return_value = [self.test_user]
        mock_rec_db.mark_session_invalid.return_value = True
        
        # Mock the auth check response
        auth_response = MagicMock()
        auth_response.status_code = 200
        auth_response.json.return_value = {"IsAuthenticated": True}
        
        # Mock the verify response with a failure
        verify_response = MagicMock()
        verify_response.status_code = 403
        
        # Configure mock to return different responses
        def get_side_effect(url, **kwargs):
            if url == AUTH_CHECK_URL:
                return auth_response
            elif url == VERIFY_URL:
                return verify_response
            return MagicMock(status_code=404)
            
        mock_get.side_effect = get_side_effect
        
        # Execute the function
        check_and_refresh_sessions()
        
        # Assert that session was marked invalid
        mock_rec_db.mark_session_invalid.assert_called_once_with(self.test_user.id)

    @patch('tasks.rec_tasks.rec_db')
    @patch('requests.get')
    def test_request_exception(self, mock_get, mock_rec_db):
        """Test handling of request exceptions during authentication check."""
        # Set up mock responses and database
        mock_rec_db.get_active_users.return_value = [self.test_user]
        
        # Mock request.get to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Test error")
        
        # Execute the function (should not raise an exception)
        check_and_refresh_sessions()
        
        # Assert behavior when exception occurs
        mock_rec_db.get_active_users.assert_called_once()
        mock_rec_db.mark_session_invalid.assert_not_called()  # Should not update status on request error

    @patch('tasks.rec_tasks.RecDatabase')
    def test_setup_rec_tasks(self, mock_rec_db_class):
        """Test setup_rec_tasks initializes the database connection."""
        # Execute the function
        setup_rec_tasks()
        
        # Assert that RecDatabase was instantiated
        mock_rec_db_class.assert_called_once()


if __name__ == '__main__':
    unittest.main()