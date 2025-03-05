import random
from datetime import datetime, timedelta
import logging
from typing import Dict, List
from database.dining import DiningDatabase
from database.gyms import GymDatabase
from config.dining import OCCUSPACE_IDS
from config.gyms import FACILITY_IDS
from config.base import DATABASE_URL
from database.db import db
from flask import Flask
from models.dining import DiningCapacityHistory
from models.gyms import GymCapacityHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    db.init_app(app)
    
    return app

def generate_dining_pattern(hour: int) -> float:
    """Generate a realistic occupancy pattern for dining halls."""
    # Breakfast: 7-9am
    if 7 <= hour <= 9:
        return random.uniform(0.6, 0.9)
    # Lunch: 11am-2pm
    elif 11 <= hour <= 14:
        return random.uniform(0.7, 0.95)
    # Dinner: 5-8pm
    elif 17 <= hour <= 20:
        return random.uniform(0.7, 0.95)
    # Late night: 9pm-1am
    elif 21 <= hour <= 23:
        return random.uniform(0.4, 0.7)
    # Off-peak hours
    else:
        return random.uniform(0.1, 0.3)

def generate_gym_pattern(hour: int) -> float:
    """Generate a realistic occupancy pattern for gyms."""
    # Morning rush: 6-9am
    if 6 <= hour <= 9:
        return random.uniform(0.6, 0.85)
    # Afternoon: 2-5pm
    elif 14 <= hour <= 17:
        return random.uniform(0.4, 0.7)
    # Evening rush: 6-10pm
    elif 18 <= hour <= 22:
        return random.uniform(0.7, 0.95)
    # Late night: 10pm-1am
    elif 22 <= hour <= 23:
        return random.uniform(0.3, 0.6)
    # Off-peak hours
    else:
        return random.uniform(0.1, 0.3)

def generate_mock_dining_data(dining_db: DiningDatabase):
    """Generate and upload mock dining hall capacity data for the past week."""
    logger.info("Generating mock dining hall data...")
    
    # Get all dining halls upfront using SQLAlchemy query
    from models.dining import DiningHall
    dining_halls = {hall.slug: hall for hall in DiningHall.query.all()}
    
    # Generate data for the past 7 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # Collect all records in memory
    capacity_records = []
    
    # Generate data every 5 minutes
    current_time = start_time
    while current_time <= end_time:
        for slug in OCCUSPACE_IDS:
            # Get base capacity (random between 100-300)
            base_capacity = random.randint(100, 300)
            
            # Calculate occupants based on time of day
            occupancy_rate = generate_dining_pattern(current_time.hour)
            occupants = int(base_capacity * occupancy_rate)
            
            # Add some random variation
            occupants += random.randint(-10, 10)
            occupants = max(0, min(occupants, base_capacity))
            
            # Create record using pre-fetched hall data
            hall = dining_halls.get(slug)
            if hall:
                record = DiningCapacityHistory(
                    hall_id=hall.id,
                    occupants=occupants,
                    capacity=base_capacity,
                    last_updated=current_time
                )
                capacity_records.append(record)
            
        current_time += timedelta(minutes=5)
    
    # Batch insert all records
    try:
        db.session.bulk_save_objects(capacity_records)
        db.session.commit()
        logger.info(f"Successfully batch inserted {len(capacity_records)} dining capacity records")
    except Exception as e:
        logger.error(f"Error batch inserting dining capacity records: {e}")
        db.session.rollback()
    
    logger.info("Finished generating dining hall data")

def generate_mock_gym_data(gym_db: GymDatabase):
    """Generate and upload mock gym capacity data for the past week."""
    logger.info("Generating mock gym data...")
    
    # Get all gyms upfront using SQLAlchemy query
    from models.gyms import Gym
    gyms = {gym.slug: gym for gym in Gym.query.all()}
    
    # Define zones for each gym
    gym_zones = {
        "bfit": [
            "Weight Room",
            "Cardio Room",
            "Group Exercise Room",
            "Basketball Court"
        ],
        "john-wooden-center": [
            "Main Gym",
            "Weight Room",
            "Cardio Room",
            "Pool"
        ]
    }
    
    # Generate data for the past 7 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # Collect all records in memory
    capacity_records = []
    
    # Generate data every 5 minutes
    current_time = start_time
    while current_time <= end_time:
        for slug, zones in gym_zones.items():
            for zone in zones:
                # Get base capacity (random between 20-100)
                base_capacity = random.randint(20, 100)
                
                # Calculate occupants based on time of day
                occupancy_rate = generate_gym_pattern(current_time.hour)
                occupants = int(base_capacity * occupancy_rate)
                
                # Add some random variation
                occupants += random.randint(-5, 5)
                occupants = max(0, min(occupants, base_capacity))
                
                # Create record using pre-fetched gym data
                gym = gyms.get(slug)
                if gym:
                    record = GymCapacityHistory(
                        gym_id=gym.id,
                        zone_name=zone,
                        occupants=occupants,
                        capacity=base_capacity,
                        last_updated=current_time
                    )
                    capacity_records.append(record)
            
        current_time += timedelta(minutes=5)
    
    # Batch insert all records
    try:
        db.session.bulk_save_objects(capacity_records)
        db.session.commit()
        logger.info(f"Successfully batch inserted {len(capacity_records)} gym capacity records")
    except Exception as e:
        logger.error(f"Error batch inserting gym capacity records: {e}")
        db.session.rollback()
    
    logger.info("Finished generating gym data")

def main():
    """Main function to generate mock data within application context."""
    app = create_app()
    
    with app.app_context():
        # Initialize database handlers
        dining_db = DiningDatabase()
        gym_db = GymDatabase()
        
        logger.info("Starting mock data generation...")
        
        # Generate data for both dining halls and gyms
        generate_mock_dining_data(dining_db)
        generate_mock_gym_data(gym_db)
        
        logger.info("Mock data generation complete!")

if __name__ == "__main__":
    main()