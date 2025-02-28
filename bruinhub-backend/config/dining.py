OCCUSPACE_PREFIX = "https://testing.occuspace.io/waitz/location"
MENUS_PREFIX = "https://menu.dining.ucla.edu/Menus"

# Dining locations that support menu scraping
MENU_ENABLED_RESTAURANTS = {
    "bplate": {
        "menu_name": "BruinPlate",  # Name used in menu URL
        "scraper_type": "standard"  # standard uses the regular menu scraping logic
    },
    "deneve": {
        "menu_name": "DeNeve",
        "scraper_type": "standard"
    },
    "epicuria": {
        "menu_name": "Epicuria",
        "scraper_type": "standard"
    },
    "feast": {
        "menu_name": "FeastAtRieber",
        "scraper_type": "feast"  # feast uses special menu scraping logic
    }
}

# Occuspace IDs for all dining locations
OCCUSPACE_IDS = {
    "bplate": 77,
    "deneve": 78,
    "bruin-cafe": 79,
    "the-drey": 81,
    "rendezvous": 82,
    "study-hedrick": 83,
    "epicuria-covel": 88,
    "feast": 100,
    "epicuria-ackerman": 108
}

def supports_menu_scraping(slug: str) -> bool:
    """Check if a dining location supports menu scraping."""
    return slug in MENU_ENABLED_RESTAURANTS

def get_menu_info(slug: str) -> dict:
    """Get menu scraping information for a dining location."""
    return MENU_ENABLED_RESTAURANTS.get(slug, {}) 