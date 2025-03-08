import unittest
from unittest.mock import patch, MagicMock, call
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from tasks.scheduler import init_scheduler
from app import app


class TestTaskScheduler(unittest.TestCase):
    def setUp(self):
        # Create application context for tests
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        # Remove application context after test
        self.app_context.pop()

    @patch('tasks.scheduler.BackgroundScheduler')
    @patch('tasks.scheduler.scrape_and_store_gym_data')
    @patch('tasks.scheduler.scrape_and_store_dining_data')
    @patch('tasks.scheduler.scrape_and_store_library_data')
    @patch('tasks.scheduler.check_and_refresh_sessions')
    @patch('tasks.scheduler.attempt_reservations')
    def test_scheduler_initialization(self, mock_attempt_reservations, mock_check_sessions, 
                                     mock_library, mock_dining, mock_gym, mock_scheduler_class):
        """Test that scheduler is properly initialized with all jobs."""
        # Setup mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler_class.return_value = mock_scheduler

        # Test values for intervals
        scrape_interval = 300  # 5 minutes
        refresh_interval = 900  # 15 minutes

        # Initialize the scheduler
        scheduler = init_scheduler(app, scrape_interval, refresh_interval)

        # Verify the scheduler was created
        mock_scheduler_class.assert_called_once()
        
        # Verify add_job was called with the correct intervals
        # Jobs are wrapped so we need to check the interval parameters
        calls = mock_scheduler.add_job.call_args_list
        
        # Verify gym job was added with correct interval
        self.assertIn(call(unittest.mock.ANY, 'interval', seconds=scrape_interval), calls)
        
        # Verify dining job was added with correct interval
        self.assertIn(call(unittest.mock.ANY, 'interval', seconds=scrape_interval), calls)
        
        # Verify library job was added with correct interval
        self.assertIn(call(unittest.mock.ANY, 'interval', seconds=scrape_interval), calls)
        
        # Verify session refresh job was added with correct interval
        self.assertIn(call(unittest.mock.ANY, 'interval', seconds=refresh_interval, id="session_refresh"), calls)

        # Verify the scheduler was started
        mock_scheduler.start.assert_called_once()
        
        # Verify the function returns the scheduler
        self.assertEqual(scheduler, mock_scheduler)

    @patch('tasks.scheduler.BackgroundScheduler')
    def test_job_context_wrappers(self, mock_scheduler_class):
        """Test that job wrappers properly apply app context."""
        # Setup mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler_class.return_value = mock_scheduler
        
        with patch('tasks.scheduler.scrape_and_store_gym_data') as mock_gym_job:
            # Initialize the scheduler
            init_scheduler(app, 300, 900)
            
            # Get the wrapped gym job function
            gym_job_wrapper = mock_scheduler.add_job.call_args_list[0][0][0]
            
            # Execute the wrapper
            gym_job_wrapper()
            
            # Verify the original function was called within app context
            mock_gym_job.assert_called_once()

    @patch('tasks.scheduler.BackgroundScheduler')
    @patch('tasks.scheduler.check_and_refresh_sessions')
    def test_session_refresh_job_execution(self, mock_check_sessions, mock_scheduler_class):
        """Test that session refresh job executes the appropriate function."""
        # Setup mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler_class.return_value = mock_scheduler
        
        # Initialize the scheduler
        init_scheduler(app, 300, 900)
        
        # Find the session refresh job wrapper
        session_job_wrapper = None
        for call_args in mock_scheduler.add_job.call_args_list:
            if len(call_args[1]) >= 1 and call_args[1].get('id') == 'session_refresh':
                session_job_wrapper = call_args[0][0]
                break
        
        self.assertIsNotNone(session_job_wrapper, "Session refresh job not found")
        
        # Execute the wrapper
        session_job_wrapper()
        
        # Verify the check_and_refresh_sessions function was called
        mock_check_sessions.assert_called_once()

    @patch('tasks.scheduler.BackgroundScheduler')
    def test_scheduler_shutdown(self, mock_scheduler_class):
        """Test that scheduler can be properly shut down."""
        # Setup mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler_class.return_value = mock_scheduler
        
        # Initialize the scheduler
        scheduler = init_scheduler(app, 300, 900)
        
        # Verify we can shut down the scheduler
        scheduler.shutdown()
        mock_scheduler.shutdown.assert_called_once()

    @patch('tasks.scheduler.BackgroundScheduler', autospec=True)
    @patch('tasks.scheduler.scrape_and_store_gym_data')
    @patch('tasks.scheduler.scrape_and_store_dining_data')
    @patch('tasks.scheduler.scrape_and_store_library_data')
    def test_multiple_scraping_jobs(self, mock_library, mock_dining, mock_gym, MockScheduler):
        """Test that all scraping jobs are added with the same interval."""
        # Create a real scheduler instance for more detailed testing
        mock_scheduler = MockScheduler.return_value
        
        # Initialize the scheduler
        scrape_interval = 300
        init_scheduler(app, scrape_interval, 900)
        
        # Count how many jobs were added with the scrape interval
        scrape_job_count = 0
        for call_args in mock_scheduler.add_job.call_args_list:
            if len(call_args[1]) >= 1 and call_args[1].get('seconds') == scrape_interval:
                scrape_job_count += 1
        
        # We expect 3 scraping jobs (gym, dining, library)
        self.assertEqual(scrape_job_count, 3, "Expected exactly 3 scraping jobs")

    @patch('tasks.scheduler.BackgroundScheduler')
    def test_custom_intervals(self, mock_scheduler_class):
        """Test that scheduler accepts custom intervals."""
        # Setup mock scheduler
        mock_scheduler = MagicMock(spec=BackgroundScheduler)
        mock_scheduler_class.return_value = mock_scheduler
        
        # Use custom intervals
        scrape_interval = 60  # 1 minute
        refresh_interval = 120  # 2 minutes
        
        # Initialize the scheduler with custom intervals
        init_scheduler(app, scrape_interval, refresh_interval)
        
        # Verify jobs were added with custom intervals
        scrape_jobs = [call for call in mock_scheduler.add_job.call_args_list 
                      if 'seconds' in call[1] and call[1]['seconds'] == scrape_interval]
        refresh_jobs = [call for call in mock_scheduler.add_job.call_args_list 
                       if 'seconds' in call[1] and call[1]['seconds'] == refresh_interval]
        
        self.assertEqual(len(scrape_jobs), 3, "Expected 3 jobs with scrape interval")
        self.assertEqual(len(refresh_jobs), 1, "Expected 1 job with refresh interval")


if __name__ == '__main__':
    unittest.main()