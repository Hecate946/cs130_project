import requests
from bs4 import BeautifulSoup

def fetch_booking_dates(cookies, headers):
    """
    Fetches available booking dates from the UCLA recreation booking system.
    Works on both mobile and desktop by merging duplicate entries.

    Args:
        cookies (dict): A dictionary containing session cookies.
        headers (dict): A dictionary containing request headers.

    Returns:
        list: A list of dictionaries with available booking dates.
    """

    url = "https://secure.recreation.ucla.edu/booking/02a10035-6fd3-48b1-9a1f-648f6368c09a/dates"
    
    try:
        # Send request to fetch booking dates
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # Raise an error if the request fails

        # Parse HTML response
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract both mobile and desktop sections
        mobile_section = soup.find("div", class_="d-block d-lg-none")
        desktop_section = soup.find("div", class_="d-none d-lg-block")

        # Find all buttons in both sections
        mobile_buttons = mobile_section.find_all("button", class_="single-date-select-button") if mobile_section else []
        desktop_buttons = desktop_section.find_all("button", class_="single-date-select-button") if desktop_section else []

        # Merge data by `data-button-index`
        date_dict = {}

        for button in mobile_buttons + desktop_buttons:  # Combine both lists
            index = button.get("data-button-index")

            if index not in date_dict:  # Only store one instance per index
                date_dict[index] = {
                    "index": index,
                    "year": button.get("data-year"),
                    "month": button.get("data-month"),
                    "day": button.get("data-day"),
                    "date_text": button.get("data-date-text")
                }

        return list(date_dict.values())  # Convert dictionary back to a list

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching booking dates: {e}")
        return None


# Example Usage:
cookies = {
    ".AspNet.ApplicationCookie": "tYrYcK6OXP82W4z9mPqeQQ2RcrrBg8CZqbhKSir8T9uspIT-1KSakzY8Ch_6EjOlHwtXhFXQ4EmoMDxz0sMbPlZGV-kuoprNQeTdmTgjSBF5O4iPgDU4LGNKhhWDWPnP8ky1_HvMbqBVWMMe35QVXAzCmDCnNeUS9IDEcwoq46Wd_hcjpMzi0sjZEaD9esyIWk14QSnbOMdswloB-ntfccdq445l-t840gUXOv68jxGW3ag8Abnwq5-Yy3IrCcb4oqFjTtvY_CiwlJSSBannQ7NAhcDop6NLhw-4dwiFfv3IskyWLIOMAQXj2gAT9khdHYPazJAXkbYAcxo-rknSt2lVpImUP2l4NexW14QI_JZOnjkaZHcb7dUiiZmhURzr"
}
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "X-Requested-With": "XMLHttpRequest",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

# Fetch and print available dates
available_dates = fetch_booking_dates(cookies, headers)
if available_dates:
    for date in available_dates:
        print(date)
