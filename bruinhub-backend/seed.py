from datetime import datetime
from app import app
from models.library import db, Library, LibraryRoom, LibraryBooking
from config.library import (
    DATABASE_URL,
    POWELL,
    YRL,
    MUSIC_LIBRARY,
    BIOMEDICAL,
    SEL,
    MEDIA_LAB
)

DB_URL = DATABASE_URL

with app.app_context():
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

    print("Database seeded successfully.")
