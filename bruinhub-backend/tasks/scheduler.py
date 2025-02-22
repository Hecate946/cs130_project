from apscheduler.schedulers.background import BackgroundScheduler
from .gym_tasks import scrape_and_store_gym_data
from .dining_tasks import scrape_and_store_dining_data
from .library_tasks import scrape_and_store_library_data

def init_scheduler(app, scrape_interval: int) -> BackgroundScheduler:
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

    # Add jobs with wrapped context
    # scheduler.add_job(gym_job, 'interval', seconds=scrape_interval)
    # scheduler.add_job(dining_job, 'interval', seconds=scrape_interval)
    scheduler.add_job(library_job, 'interval', seconds=scrape_interval)

    scheduler.start()
    return scheduler