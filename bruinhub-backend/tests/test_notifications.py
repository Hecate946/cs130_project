import pytest
from models.notifications import DeviceToken

DEFAULT_PREFERENCES = {
    "capacity": {"enabled": True, "threshold": 50},
    "closing": {"enabled": True, "minutes_before": 30}
}

def test_default_preferences():
    # When no preferences are provided, the default should be set.
    token = DeviceToken(push_token="abcdefghij1234567890", device_type="ios")
    assert token.preferences == DEFAULT_PREFERENCES

def test_custom_preferences():
    # When custom preferences are provided, they should be stored correctly.
    custom_prefs = {
        "capacity": {"enabled": False, "threshold": 30},
        "closing": {"enabled": False, "minutes_before": 10}
    }
    token = DeviceToken(push_token="unique_token_abcdef", device_type="android", preferences=custom_prefs)
    assert token.preferences == custom_prefs

def test_repr_contains_truncated_push_token():
    push_token = "123456789012345"
    token = DeviceToken(push_token=push_token, device_type="ios")
    repr_str = repr(token)
    # Check that the repr string contains "DeviceToken" and the truncated push token
    assert "DeviceToken" in repr_str
    assert push_token[:10] in repr_str

def test_empty_preferences_defaults_to_default():
    token = DeviceToken(push_token="empty_pref_token", device_type="ios", preferences={})
    assert token.preferences == DEFAULT_PREFERENCES

def test_user_id_assignment():
    # Check that the user_id is correctly assigned.
    token = DeviceToken(push_token="user_id_token", device_type="ios", user_id=42)
    assert token.user_id == 42

def test_preferences_immutable_after_init():
    # Ensure changes to the original custom preferences after initialization do not alter token.preferences.
    custom_prefs = {
        "capacity": {"enabled": False, "threshold": 30},
        "closing": {"enabled": False, "minutes_before": 10}
    }
    token = DeviceToken(push_token="immutable_token", device_type="android", preferences=custom_prefs.copy())
    # Modify the original dict
    custom_prefs["capacity"]["enabled"] = True
    expected = {
        "capacity": {"enabled": False, "threshold": 30},
        "closing": {"enabled": False, "minutes_before": 10}
    }
    assert token.preferences == expected

if __name__ == '__main__':
    pytest.main()