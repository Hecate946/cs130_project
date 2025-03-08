import pytest
from unittest.mock import patch, MagicMock
import json
import requests
from datetime import datetime

from scrapers.gyms import GymScrapers
from config.gyms import FACILITY_IDS, FACILITY_COUNT_URL
from config.gyms_static import GYM_HOURS


# Sample data for tests
SAMPLE_FACILITY_DATA = [
    {
        "FacilityId": 803,  # BFIT
        "LocationName": "Weight Room",
        "LastCount": 25,
        "TotalCapacity": 50,
        "IsClosed": False,
        "LastUpdatedDateAndTime": "2025-03-08T10:30:00Z"
    },
    {
        "FacilityId": 803,  # BFIT
        "LocationName": "Cardio Room",
        "LastCount": 15,
        "TotalCapacity": 40,
        "IsClosed": False,
        "LastUpdatedDateAndTime": "2025-03-08T10:30:00Z"
    },
    {
        "FacilityId": 802,  # John Wooden Center
        "LocationName": "Main Gym",
        "LastCount": 45,
        "TotalCapacity": 100,
        "IsClosed": False,
        "LastUpdatedDateAndTime": "2025-03-08T10:32:00Z"
    },
    {
        "FacilityId": 999,  # Invalid facility
        "LocationName": "Test Zone",
        "LastCount": 5,
        "TotalCapacity": 10,
        "IsClosed": True,
        "LastUpdatedDateAndTime": "2025-03-08T10:32:00Z"
    }
]


class TestGymScrapers:
    """Test suite for the GymScrapers class"""

    @patch('requests.get')
    def test_get_facility_counts(self, mock_get):
        """Test retrieving raw facility count data from the API"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_FACILITY_DATA
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Call method under test
        result = GymScrapers.get_facility_counts()

        # Verify
        mock_get.assert_called_once_with(FACILITY_COUNT_URL)
        assert result == SAMPLE_FACILITY_DATA
        assert isinstance(result, list)
        assert len(result) == 4

    @patch('requests.get')
    def test_get_facility_counts_error_handling(self, mock_get):
        """Test error handling when API call fails"""
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        # Call method under test
        result = GymScrapers.get_facility_counts()

        # Verify error handling
        assert result == [{}]

    def test_filter_facility_zones(self):
        """Test filtering and formatting of facility zones"""
        # Test with BFIT facility ID
        bfit_zones = GymScrapers.filter_facility_zones(SAMPLE_FACILITY_DATA, 803)
        
        # Verify correct filtering and data structure
        assert len(bfit_zones) == 2
        assert bfit_zones[0]["zone_name"] == "Weight Room"
        assert bfit_zones[0]["occupants"] == 25
        assert bfit_zones[0]["capacity"] == 50
        assert not bfit_zones[0]["open"] == False  # Not closed = open
        assert bfit_zones[0]["last_updated"] == "2025-03-08T10:30:00Z"

    def test_filter_facility_zones_empty_input(self):
        """Test filtering with empty input data"""
        result = GymScrapers.filter_facility_zones([], 803)
        assert result == []

    def test_filter_facility_zones_no_matching_facility(self):
        """Test filtering when no zones match the facility ID"""
        result = GymScrapers.filter_facility_zones(SAMPLE_FACILITY_DATA, 12345)
        assert result == []

    def test_filter_facility_zones_error_handling(self):
        """Test error handling in filter_facility_zones"""
        # Provide malformed data missing required fields
        malformed_data = [{"FacilityId": 803}]  # Missing other fields
        
        result = GymScrapers.filter_facility_zones(malformed_data, 803)
        assert result == []

    @patch('scrapers.gyms.GymScrapers.get_facility_counts')
    def test_scrape_facility_counts(self, mock_get_counts):
        """Test the main scraping function for gym facility counts"""
        # Setup mock
        mock_get_counts.return_value = SAMPLE_FACILITY_DATA
        
        # Call method under test
        result = GymScrapers.scrape_facility_counts()
        
        # Verify
        assert isinstance(result, dict)
        assert "bfit" in result
        assert "john-wooden-center" in result
        
        # Check BFIT data
        assert len(result["bfit"]) == 2
        assert result["bfit"][0]["zone_name"] == "Weight Room"
        
        # Check JWC data
        assert len(result["john-wooden-center"]) == 1
        assert result["john-wooden-center"][0]["zone_name"] == "Main Gym"

    @patch('scrapers.gyms.GymScrapers.get_facility_counts')
    def test_scrape_facility_counts_empty_data(self, mock_get_counts):
        """Test handling of empty data in scrape_facility_counts"""
        # Setup mock to return empty data
        mock_get_counts.return_value = []
        
        result = GymScrapers.scrape_facility_counts()
        
        # Should return empty dict for each facility
        assert isinstance(result, dict)
        assert all(len(zones) == 0 for zones in result.values())

    @patch('scrapers.gyms.GymScrapers.get_facility_counts')
    def test_scrape_facility_counts_error_handling(self, mock_get_counts):
        """Test error handling in scrape_facility_counts"""
        # Setup mock to raise exception
        mock_get_counts.side_effect = Exception("Unexpected error")
        
        result = GymScrapers.scrape_facility_counts()
        
        # Should handle error and return empty dict
        assert result == {}

    def test_get_static_hours(self):
        """Test retrieving static hours data"""
        hours = GymScrapers.get_static_hours()
        
        # Verify returned data structure
        assert hours == GYM_HOURS
        assert "bfit" in hours
        assert "john-wooden-center" in hours
        assert "regular_hours" in hours["bfit"]
        assert "special_hours" in hours["bfit"]
        
        # Check specific hours entry
        assert "Monday" in hours["bfit"]["regular_hours"]
        assert isinstance(hours["bfit"]["special_hours"], dict)
        
        # Basic format validation for hours
        sample_hours = hours["bfit"]["regular_hours"]["Monday"]
        assert " - " in sample_hours  # Hours should have format like "6:00 AM - 1:00 AM"

    def test_gym_hours_data_validity(self):
        """Test that gym hours data contains valid time formats"""
        hours = GymScrapers.get_static_hours()
        
        # Check a few sample dates/times to ensure they have valid format
        for gym, data in hours.items():
            for day, time_range in data["regular_hours"].items():
                assert time_range == "CLOSED" or " - " in time_range
                
            # Check a sample of special hours if available
            if data["special_hours"]:
                sample_date = next(iter(data["special_hours"]))
                time_range = data["special_hours"][sample_date]
                assert time_range == "CLOSED" or " - " in time_range