from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DiningScrapers:
    @staticmethod
    def scrape_dining_halls() -> Dict:
        """Simulates scraping UCLA dining hall data"""
        logger.info("Starting dining hall data scrape")
        try:
            # Dummy data for dining halls
            dining_data = {
                "Epicuria": {
                    "Capri": ["Spinach Tortellini", "Shrimp Alfredo Pasta"],
                    "Psistaria": ["Vegetarian Meatball Sandwich"],
                    "Mezze": ["Roasted Carrots"],
                    "Alimenti": ["Braised Lamb", "Polenta"],
                    "capacity": 100,
                    "hours": {
                        "Monday": "7:00 AM - 10:00 PM",
                        "Tuesday": "7:00 AM - 10:00 PM",
                        "Wednesday": "7:00 AM - 10:00 PM",
                        "Thursday": "7:00 AM - 10:00 PM",
                        "Friday": "7:00 AM - 9:00 PM",
                        "Saturday": "8:00 AM - 8:00 PM",
                        "Sunday": "8:00 AM - 8:00 PM",
                    },
                },
                "De Neve": {
                    "Flex Bar": ["Chicken Thigh"],
                    "The Front Burner": ["Pork Pozole", "Vegetarian Pozole"],
                    "The Kitchen": ["Carne Asada Fries"],
                    "The Pizzeria": ["Garlic Chicken Pizza", "Mushroom Pizza"],
                    "The Grill": ["DFC"],
                    "capacity": 20,
                    "hours": {
                        "Monday": "7:30 AM - 9:30 PM",
                        "Tuesday": "7:30 AM - 9:30 PM",
                        "Wednesday": "7:30 AM - 9:30 PM",
                        "Thursday": "7:30 AM - 9:30 PM",
                        "Friday": "7:30 AM - 9:00 PM",
                        "Saturday": "8:30 AM - 8:00 PM",
                        "Sunday": "8:30 AM - 8:00 PM",
                    },
                },
                "Bruin Plate": {
                    "Freshly Bowled": ["Roasted Vegetables"],
                    "Harvest": ["Quinoa Salad"],
                    "Simply Grilled": ["Grilled Chicken"],
                    "capacity": 70,
                    "hours": {
                        "Monday": "7:00 AM - 10:00 PM",
                        "Tuesday": "7:00 AM - 10:00 PM",
                        "Wednesday": "7:00 AM - 10:00 PM",
                        "Thursday": "7:00 AM - 10:00 PM",
                        "Friday": "7:00 AM - 9:00 PM",
                        "Saturday": "8:00 AM - 8:00 PM",
                        "Sunday": "8:00 AM - 8:00 PM",
                    },
                },
            }

            logger.info("Successfully scraped dining hall data")
            return dining_data

        except Exception as e:
            logger.error(f"Error in dummy dining hall scraping: {e}", exc_info=True)
            return {}
