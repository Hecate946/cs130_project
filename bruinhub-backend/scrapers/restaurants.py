import requests
from bs4 import BeautifulSoup
from test.test_dis import get_tb
from config import OCCUSPACE_PREFIX, MENUS_PREFIX

RESTAURANTS = ["BruinPlate", "DeNeve", "Epicuria"]

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
    data = requests.get(f"{OCCUSPACE_PREFIX}/{OCCUSPACE_IDS[restaurant]}/hours").json()
    return next(rules["hours"] for rules in data["data"][0]["rules"] if rules["active"] == True)

def _occupancy(restaurant: str) -> tuple[int, int]:
    """
    Returns number of people and the capacity of the restaurant.
    """
    data = requests.get(f"{OCCUSPACE_PREFIX}/{OCCUSPACE_IDS[restaurant]}").json()
    return data["data"]["people"], data["data"]["capacity"]

def _menu(restaurant: str) -> dict[str, list[str]]:
    """
    Returns the menu for the restaurant.
    """
    soup = BeautifulSoup(
        requests.get(f"{MENUS_PREFIX}/{restaurant}").text, "lxml"
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
