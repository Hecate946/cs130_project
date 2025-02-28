from datetime import datetime
from app import app
from models.library import db, Library, LibraryRoom, LibraryBooking
from models.dining import DiningHall
from models.gyms import Gym
from config.library import (
    POWELL,
    YRL,
    MUSIC_LIBRARY,
    BIOMEDICAL,
    SEL,
    MEDIA_LAB
)
from config.dining import OCCUSPACE_IDS
from config.gyms import FACILITY_IDS
from config.base import DATABASE_URL
from scrapers.gyms import GymScrapers

DB_URL = DATABASE_URL

with app.app_context():
    # Seed Libraries
    libraries_data = [
        {
            "name": POWELL,
            "slug": "powell",
            "location": "10740 Dickson Plaza Los Angeles, CA 90095-1450"
        },
        {
            "name": YRL,
            "slug": "yrl",
            "location": "280 Charles E. Young Drive, North Los Angeles, CA 90095-1575"
        },
        {
            "name": MUSIC_LIBRARY,
            "slug": "music-library",
            "location": "1102 Schoenberg Music Building Los Angeles, CA 90095-1490"
        },
        {
            "name": BIOMEDICAL,
            "slug": "biomedical",
            "location": "12-077 Center for Health Sciences Los Angeles, CA 90095-1798"
        },
        {
            "name": SEL,
            "slug": "sel",
            "location": "8270 Boelter Hall Los Angeles, CA 90095-154"
        },
        {
            "name": MEDIA_LAB,
            "slug": "media-lab",
            "location": "2100A YRL Los Angeles, CA 90095-1575"
        }
    ]

    print("Seeding libraries...")
    for lib in libraries_data:
        # Check if a library with the given slug already exists
        existing = Library.query.filter_by(slug=lib["slug"]).first()
        if not existing:
            new_library = Library(
                name=lib["name"],
                slug=lib["slug"],
                location=lib["location"]
            )
            db.session.add(new_library)
            db.session.commit()
            print(f"Library '{lib['slug']}' created.")
        else:
            print(f"Library '{lib['slug']}' already exists.")

    # Seed Dining Halls
    print("\nSeeding dining halls...")
    for slug in OCCUSPACE_IDS:  # Now using OCCUSPACE_IDS which contains all dining locations
        existing = DiningHall.query.filter_by(slug=slug).first()
        if not existing:
            new_dining = DiningHall(
                slug=slug,
                menu={},  # Empty JSON object
                hours_today={}  # Empty JSON object
            )
            db.session.add(new_dining)
            db.session.commit()
            print(f"Dining hall '{slug}' created.")
        else:
            print(f"Dining hall '{slug}' already exists.")

    # Seed Gyms
    print("\nSeeding gyms...")
    gym_scraper = GymScrapers()
    hours_data = gym_scraper.get_static_hours()

    for slug in FACILITY_IDS:  # Use FACILITY_IDS from config
        existing = Gym.query.filter_by(slug=slug).first()
        hours = hours_data.get(slug, {"regular_hours": {}, "special_hours": {}})
        
        if not existing:
            new_gym = Gym(
                slug=slug,
                regular_hours=hours["regular_hours"],
                special_hours=hours.get("special_hours", {})
            )
            db.session.add(new_gym)
            db.session.commit()
            print(f"Gym '{slug}' created with hours.")
        else:
            # Update hours for existing gyms
            existing.regular_hours = hours["regular_hours"]
            existing.special_hours = hours.get("special_hours", {})
            db.session.commit()
            print(f"Updated hours for existing gym '{slug}'.")

    print("\nDatabase seeded successfully.")
