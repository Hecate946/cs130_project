"""
Scrapes occupancy data from Connect2Concepts API for Bruin Fit and
John Wooden Center, as well as Occuspace for Powell and the restaurants.
"""

# Occuspace info for UCLA: https://testing.occuspace.io/waitz/customer/21/locations

import requests
from bs4 import BeautifulSoup
from test.test_dis import get_tb

# Activity data for John Wooden (there's a diff, similar URL for BFit): https://www.connect2mycloud.com/Widgets/Data/locationCount?type=bar&facility=803&key=73829a91-48cb-4b7b-bd0b-8cf4134c04cd

RESTAURANTS = ["BruinPlate", "DeNeve", "Epicuria"]

# From https://testing.occuspace.io/waitz/customer/21/locations
OCCUSPACE_IDS: dict[str, int] = {
    "Powell CLICC": 104,
    "The Drey": 81,
    "Feast": 100,
    "Epicuria": 88,
    "Epicuria at Ackerman": 108,
    "Bruin Cafe": 79,
    "Rendezvous": 82,
    "BruinPlate": 77,
    "DeNeve": 78,
    "The Study": 83,
}

# From https://testing.occuspace.io/waitz/customer/21/locations
OCCUSPACE_IDS: dict[str, int] = {
    "Epicuria": 88,
    "BruinPlate": 77,
    "DeNeve": 78,
}


def _hours_today(restaurant: str) -> list[str]:
    """
    Returns the hours of operation that apply today
    """
    data = requests.get(f"https://testing.occuspace.io/waitz/location/{OCCUSPACE_IDS[restaurant]}/hours").json()
    return next(rules["hours"] for rules in data["data"][0]["rules"] if rules["active"] == True)

def _occupancy(restaurant: str) -> tuple[int, int]:
    """
    Returns number of people and the capacity of the restaurant.
    """
    data = requests.get(f"https://testing.occuspace.io/waitz/location/{OCCUSPACE_IDS[restaurant]}").json()
    return data["data"]["people"], data["data"]["capacity"]

def _menu(restaurant: str) -> dict[str, list[str]]:
    """
    Returns the menu for the restaurant.
    """
    soup = BeautifulSoup(
        requests.get(f"https://menu.dining.ucla.edu/Menus/{restaurant}").text, "lxml"
    )

    return {
        str(section.contents[0]).strip(): list(
            map(lambda elem: elem.text, section.select("a"))
        )
        for section in soup.select("li.sect-item")
    }

def get_restaurants():
    """
    Returns occupany, menu, and hours data for all restaurants
    """
    occupants, capacity = _occupancy("BruinPlate")
    return {
        restaurant: {
            "hours_today": _hours_today(restaurant),
            "occupants": occupants,
            "capacity": capacity,
            "menu": _menu(restaurant),
        }
        for restaurant in RESTAURANTS
    }


if __name__ == "__main__":
    print(get_restaurants())
