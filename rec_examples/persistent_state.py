import time
import requests

# TODO: ensure user clicking around doesn't mess this up.

# URLs
AUTH_CHECK_URL = "https://secure.recreation.ucla.edu/account/IsAuthenticated"
VERIFY_URL = "https://secure.recreation.ucla.edu/api/issuspended/booking"

# Headers template (User-Agent and common headers)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'X-Requested-With': 'XMLHttpRequest',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

COOKIE = "ncKCxbMsyN_MD__A3jHtwtnsOAFI7c16YbBMg7JTvZtFxXCRmkuEGxiXpYQytKeMwvh2QQiVuhEysqQRoAWYwvcYKU8BlamSYcghqHZ8q0c_XTlE_NGWDviAQF-YUYIu8_U6-5Q1eE0aQIcODmqioLbFFf_NbF6s_E677Lde458oYorj_HP09O8Mdg-TOV8D3xTpdjhxNGs9oI6vGoiHG9PsRoNXzNO-7Zezq6E9n6OzOBy2L2EypRVW42TMrqOBduwOZviIRAy_JgXSBe7iZTz8YmFR6EHgslOZt9CITz09XIJKj5C4fQsmGNXN3m9ZSMMGqr6xw1jsCyGtpcMgBh_E3Y8Qqeo5fP3MSwKF6w0QblsVIzAWuPGcK5eswT2p"
# Initial cookies (replace with actual values)
COOKIES = {
    '.AspNet.ApplicationCookie': COOKIE
}

def check_auth_and_update_cookie():
    """Checks authentication status and updates session cookies if needed."""
    global COOKIES  # To update the session cookie
    
    print("🔄 Checking authentication status...")
    
    try:
        # Send request to check if user is authenticated
        auth_response = requests.get(AUTH_CHECK_URL, headers=HEADERS, cookies=COOKIES)
        auth_response.raise_for_status()
        
        # Expecting a JSON response
        is_authenticated = auth_response.json()
        
        if is_authenticated["IsAuthenticated"] == True:
            print("✅ User is authenticated.")
            
            # Check if a new `.AspNet.ApplicationCookie` is set
            new_cookies = auth_response.cookies.get_dict()
            if '.AspNet.ApplicationCookie' in new_cookies:
                print("🍪 New authentication cookie received. Updating session...")
                COOKIES['.AspNet.ApplicationCookie'] = new_cookies['.AspNet.ApplicationCookie']
            
            # Verify new cookie by calling the API
            verify_response = requests.get(VERIFY_URL, headers=HEADERS, cookies=COOKIES)
            verify_response.raise_for_status()
            
            if verify_response.status_code == 200:
                print("🔹 New cookie works. Session is valid.")
            else:
                print("⚠️ New cookie did not work. Status:", verify_response.status_code)

        else:
            print("❌ User is NOT authenticated. Re-login might be required.")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error occurred: {e}")

# Run every few minutes
while True:
    check_auth_and_update_cookie()
    time.sleep(300)  # Run every 1000 seconds (adjust as needed)
