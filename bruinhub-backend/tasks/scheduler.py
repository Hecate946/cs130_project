from apscheduler.schedulers.background import BackgroundScheduler
from .gym_tasks import scrape_and_store_gym_data
from .dining_tasks import scrape_and_store_dining_data

def init_scheduler(scrape_interval: int) -> BackgroundScheduler:
    """Initialize the task scheduler with all periodic tasks"""
    scheduler = BackgroundScheduler()

    # Add gym scraping task
    scheduler.add_job(
        func=scrape_and_store_gym_data, trigger="interval", seconds=scrape_interval
    )
    scheduler.add_job(
        func=scrape_and_store_dining_data, trigger="interval", seconds=scrape_interval
    )

    # Add other periodic tasks here as needed

    scheduler.start()
    return scheduler
