 #!/usr/bin/env python
"""
Script to test the notifications service without starting the full application.
This will simulate various notification events for testing purposes.
"""

import requests
import json
import sys
import time
import argparse

BASE_URL = "http://localhost:5002"  # Change this if running on a different port or host

def print_response(response):
    """Print a formatted API response"""
    try:
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error parsing response: {str(e)}")
        print(response.text)

def register_device(push_token, device_type="ios"):
    """Register a device for push notifications"""
    print("\n=== Registering Device ===")
    response = requests.post(
        f"{BASE_URL}/api/notifications/register",
        json={
            "pushToken": push_token,
            "deviceType": device_type,
            "preferences": {
                "capacity": {"enabled": True, "threshold": 50},
                "closing": {"enabled": True, "minutes_before": 30}
            }
        }
    )
    print_response(response)
    return response.ok

def send_test_notification(push_token):
    """Send a test notification to a device"""
    print("\n=== Sending Test Notification ===")
    response = requests.post(
        f"{BASE_URL}/api/notifications/send-test",
        json={
            "pushToken": push_token,
            "title": "BruinHub Test",
            "message": "This is a test notification from the test script!",
            "data": {"screen": "NotificationsScreen"}
        }
    )
    print_response(response)
    return response.ok

def simulate_capacity_event(facility_name, capacity):
    """Simulate a capacity notification event"""
    print(f"\n=== Simulating Capacity Event ({facility_name}: {capacity}%) ===")
    response = requests.post(
        f"{BASE_URL}/api/notifications/simulate-event",
        json={
            "eventType": "capacity",
            "facilityName": facility_name,
            "currentCapacity": capacity
        }
    )
    print_response(response)
    return response.ok

def simulate_closing_event(facility_name, minutes):
    """Simulate a closing notification event"""
    print(f"\n=== Simulating Closing Event ({facility_name}: {minutes} minutes) ===")
    response = requests.post(
        f"{BASE_URL}/api/notifications/simulate-event",
        json={
            "eventType": "closing",
            "facilityName": facility_name,
            "minutesUntilClose": minutes
        }
    )
    print_response(response)
    return response.ok

def check_service_health():
    """Check if the notification service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("Notification service is running")
            return True
        else:
            print("Notification service returned an error")
            print_response(response)
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to notification service")
        print(f"Make sure the service is running at {BASE_URL}")
        return False

def main():
    """Main function to run the test script"""
    parser = argparse.ArgumentParser(description="Test the BruinHub notification service")
    parser.add_argument("--token", "-t", required=True, help="Expo push token for testing")
    parser.add_argument("--device", "-d", default="ios", choices=["ios", "android"], help="Device type")
    
    args = parser.parse_args()
    
    push_token = args.token
    device_type = args.device
    
    if not check_service_health():
        sys.exit(1)
    
    # Register the device
    if not register_device(push_token, device_type):
        print("Failed to register device, aborting tests")
        sys.exit(1)
    
    # Wait a bit before proceeding
    time.sleep(1)
    
    # Send a test notification
    send_test_notification(push_token)
    
    # Wait for notification to be delivered
    print("\nWaiting 5 seconds for notification to be delivered...")
    time.sleep(5)
    
    # Simulate various events
    simulate_capacity_event("BFit Gym", 40)
    time.sleep(5)
    
    simulate_closing_event("Wooden Center", 15)
    
    print("\nTest script completed")

if __name__ == "__main__":
    main()