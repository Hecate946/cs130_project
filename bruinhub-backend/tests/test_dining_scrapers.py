import pytest
from unittest.mock import patch, MagicMock
from scrapers.dining import DiningScrapers
from config.dining import OCCUSPACE_PREFIX, MENUS_PREFIX


# Add this fixture to filter BeautifulSoup warnings
@pytest.fixture(autouse=True)
def suppress_bs4_warnings():
    import warnings

    # Filter the specific BeautifulSoup LXML DeprecationWarning
    warnings.filterwarnings(
        "ignore",
        message="The 'strip_cdata' option of HTMLParser()",
        category=DeprecationWarning,
    )


@patch("scrapers.dining.requests.get")
def test_get_hours_today(mock_get):
    """Test fetching hours from Occuspace API"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "rules": [
                    {"active": True, "hours": {"open": "7:00 AM", "close": "9:00 PM"}}
                ]
            }
        ]
    }
    mock_get.return_value = mock_response

    # Call the method
    hours = DiningScrapers._get_hours_today("bplate")

    # Assertions
    assert hours == {"open": "7:00 AM", "close": "9:00 PM"}
    mock_get.assert_called_once()


@patch("scrapers.dining.requests.get")
def test_get_occupancy(mock_get):
    """Test fetching occupancy from Occuspace API"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"people": 50, "capacity": 200}}
    mock_get.return_value = mock_response

    # Call the method
    occupants, capacity = DiningScrapers._get_occupancy("bplate")

    # Assertions
    assert occupants == 50
    assert capacity == 200
    mock_get.assert_called_once()


@patch("scrapers.dining.requests.get")
def test_get_standard_menu(mock_get):
    """Test parsing standard menu format"""
    # Setup mock HTML response
    mock_html = """
    <html>
        <body>
            <li class="sect-item">Breakfast<a>Eggs</a><a>Toast</a></li>
            <li class="sect-item">Lunch<a>Sandwich</a><a>Salad</a></li>
        </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = mock_html
    mock_get.return_value = mock_response

    # Call the method
    menu = DiningScrapers._get_standard_menu("BruinPlate")

    # Assertions
    assert "Breakfast" in menu
    assert "Lunch" in menu
    assert "Eggs" in menu["Breakfast"]
    assert "Sandwich" in menu["Lunch"]


@patch("scrapers.dining.DiningScrapers._get_hours_today")
@patch("scrapers.dining.DiningScrapers._get_occupancy")
@patch("scrapers.dining.DiningScrapers._get_menu")
def test_scrape_dining_halls(mock_menu, mock_occupancy, mock_hours):
    """Test main scraping function for dining halls"""
    # Setup mocks
    mock_hours.return_value = {"open": "7:00 AM", "close": "9:00 PM"}
    mock_occupancy.return_value = (50, 200)
    mock_menu.return_value = {"Breakfast": ["Eggs", "Toast"]}

    # Call the method
    scraper = DiningScrapers()
    result = scraper.scrape_dining_halls()

    # Check the structure for first dining hall (exact contents will depend on OCCUSPACE_IDS)
    if result:
        first_hall = next(iter(result.values()))
        assert "menu" in first_hall
        assert "capacity" in first_hall
        assert "occupants" in first_hall
        assert "hours_today" in first_hall
