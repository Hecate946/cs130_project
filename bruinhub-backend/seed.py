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
    powell = Library(
        name=POWELL,
        slug="powell",
        location="10740 Dickson Plaza Los Angeles, CA 90095-1450"
    )
    yrl = Library(
        name=YRL,
        slug="yrl",
        location="280 Charles E. Young Drive, North Los Angeles, CA 90095-1575"
    )
    music_library = Library(
        name=MUSIC_LIBRARY,
        slug="music-library",
        location="1102 Schoenberg Music Building Los Angeles, CA 90095-1490"
    )
    biomedical = Library(
        name=BIOMEDICAL,
        slug="biomedical",
        location="12-077 Center for Health Sciences Los Angeles, CA 90095-1798"
    )
    sel = Library(
        name=SEL,
        slug="sel",
        location="8270 Boelter Hall Los Angeles, CA 90095-154"
    )
    media_lab = Library(
        name=MEDIA_LAB,
        slug="media-lab",
        location="2100A YRL Los Angeles, CA 90095-1575"
    )


    libraries = [powell, yrl, music_library, biomedical, sel, media_lab]

    for library in libraries:
        db.session.add(library)
        db.session.commit()

    print("Database seeded successfully.")
