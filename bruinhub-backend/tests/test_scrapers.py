import pytest
from scrapers.gyms import GymScrapers
from config.gyms import FACILITY_IDS
from scrapers.dining import DiningScrapers


def test_get_facility_counts():
    """Test that we can fetch raw facility count data"""
    scraper = GymScrapers()
    data = scraper.get_facility_counts()

    # Check we got some data
    assert data, "Should receive data from facility counts API"
    assert isinstance(data, list), "Facility data should be a list"

    # Check data structure
    first_item = data[0]
    assert "FacilityId" in first_item, "Each facility should have an ID"
    assert "LocationName" in first_item, "Each facility should have a location name"
    assert "LastCount" in first_item, "Each facility should have a count"
    assert "TotalCapacity" in first_item, "Each facility should have a capacity"
    assert "LastUpdatedDateAndTime" in first_item, (
        "Each facility should have a timestamp"
    )


def test_filter_facility_zones():
    """Test that we can filter and format zone data correctly"""
    scraper = GymScrapers()

    # Create sample facility data
    sample_data = [
        {
            "FacilityId": FACILITY_IDS["bfit"],
            "LocationName": "Weight Room",
            "LastCount": 30,
            "TotalCapacity": 50,
            "IsClosed": False,
            "LastUpdatedDateAndTime": "2024-02-19T23:55:03.003",
        },
        {
            "FacilityId": 999,  # Different facility
            "LocationName": "Other Room",
            "LastCount": 10,
            "TotalCapacity": 20,
            "IsClosed": True,
            "LastUpdatedDateAndTime": "2024-02-19T23:55:03.003",
        },
    ]

    # Test filtering for BFIT
    bfit_zones = scraper.filter_facility_zones(sample_data, FACILITY_IDS["bfit"])
    assert len(bfit_zones) == 1, "Should only get BFIT zones"

    zone = bfit_zones[0]
    assert zone["zone_name"] == "Weight Room"
    assert zone["last_count"] == 30
    assert zone["percentage"] == 60  # 30/50 * 100
    assert zone["open"] is True
    assert zone["last_updated"] == "2024-02-19T23:55:03.003"


def test_scrape_facility_counts():
    """Test the main scraping function that gets all gym data"""
    scraper = GymScrapers()
    results = scraper.scrape_facility_counts()

    # Check we got data for our gyms
    assert isinstance(results, dict), "Results should be a dictionary"
    assert "bfit" in results, "Should have data for BFIT"
    assert "john-wooden-center" in results, "Should have data for Wooden Center"

    # Check structure of zone data
    for gym_slug, zones in results.items():
        assert isinstance(zones, list), f"Zones for {gym_slug} should be a list"
        if zones:  # If we got any zones
            first_zone = zones[0]
            assert "zone_name" in first_zone
            assert "last_count" in first_zone
            assert "percentage" in first_zone
            assert "open" in first_zone
            assert "last_updated" in first_zone

            # Basic validation
            assert isinstance(first_zone["percentage"], int)
            assert 0 <= first_zone["percentage"] <= 100
            assert isinstance(first_zone["last_count"], int)
            assert isinstance(first_zone["open"], bool)

def test_scrape_dining_halls():
    """Test the dining hall data fetching"""
    scraper = DiningScrapers()
    restaurants = scraper.scrape_dining_halls()

    # Check we got data for all dining locations
    assert isinstance(restaurants, dict), "Restaurants should be a dictionary"
    assert "bplate" in restaurants, "Should have data for BruinPlate"
    assert "deneve" in restaurants, "Should have data for De Neve"
    assert "epicuria-covel" in restaurants, "Should have data for Epicuria at Covel"
    assert "epicuria-ackerman" in restaurants, "Should have data for Epicuria at Ackerman"
    assert "bruin-cafe" in restaurants, "Should have data for Bruin Cafe"
    assert "the-drey" in restaurants, "Should have data for The Drey"
    assert "rendezvous" in restaurants, "Should have data for Rendezvous"
    assert "study-hedrick" in restaurants, "Should have data for Study at Hedrick"
    assert "feast" in restaurants, "Should have data for FEAST at Rieber"

    # Check structure of restaurant data
    for restaurant, data in restaurants.items():
        assert isinstance(data, dict), f"Data for {restaurant} should be a dictionary"
        assert "menu" in data, f"{restaurant} should have menu field"
        assert "capacity" in data, f"{restaurant} should have capacity field"
        assert "occupants" in data, f"{restaurant} should have occupants field"
        assert "hours_today" in data, f"{restaurant} should have hours_today field"

        # Basic validation
        assert isinstance(data["occupants"], (int, type(None))), f"Occupants for {restaurant} should be int or None"
        assert isinstance(data["capacity"], (int, type(None))), f"Capacity for {restaurant} should be int or None"
        assert isinstance(data["hours_today"], list), f"Hours for {restaurant} should be a dictionary"
        assert isinstance(data["menu"], dict), f"Menu for {restaurant} should be a dictionary"

        # Check menu structure based on restaurant type
        if restaurant == "feast":
            # Feast menu should have sections with images and items
            for section in data["menu"].values():
                assert isinstance(section, dict), "Feast menu sections should be dictionaries"
                assert "image" in section, "Feast menu sections should have image field"
                assert "items" in section, "Feast menu sections should have items field"
                assert isinstance(section["items"], list), "Feast menu items should be a list"
        elif restaurant in ["bplate", "deneve", "epicuria"]:
            # Standard menu should have sections with lists of items
            for items in data["menu"].values():
                assert isinstance(items, list), "Standard menu sections should contain lists of items"
        else:
            # Non-menu restaurants should have empty menu dict
            assert data["menu"] == {}, f"Non-menu restaurant {restaurant} should have empty menu"
