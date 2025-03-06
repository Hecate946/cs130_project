from apscheduler.schedulers.background import BackgroundScheduler
from .gym_tasks import scrape_and_store_gym_data
from .dining_tasks import scrape_and_store_dining_data
from .library_tasks import scrape_and_store_library_data
from .rec_tasks import check_and_refresh_sessions, attempt_reservations
def init_scheduler(app, scrape_interval: int, refresh_interval: int) -> BackgroundScheduler:
    """Initialize the task scheduler with all periodic tasks"""
    scheduler = BackgroundScheduler()

    # Define wrapped functions to include app context
    def gym_job():
        with app.app_context():
            scrape_and_store_gym_data()

    def dining_job():
        with app.app_context():
            scrape_and_store_dining_data()

    def library_job():
        with app.app_context():
            scrape_and_store_library_data()

    def session_refresh_job():
        with app.app_context():
            check_and_refresh_sessions()

    def reservation_attempt_job():
        with app.app_context():
            attempt_reservations()

    # Add jobs with wrapped context
    scheduler.add_job(gym_job, 'interval', seconds=scrape_interval)
    scheduler.add_job(dining_job, 'interval', seconds=scrape_interval)
    scheduler.add_job(library_job, 'interval', seconds=scrape_interval)

    scheduler.add_job(session_refresh_job, 'interval', seconds=refresh_interval, id="session_refresh")
    
    scheduler.add_job(reservation_attempt_job, 'interval', seconds=5, id="reservation_attempt")

    scheduler.start()
    return scheduler