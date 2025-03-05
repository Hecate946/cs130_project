import requests
from bs4 import BeautifulSoup

# Predefined facilities
REC_FACILITIES = [
    {"id": "02a10035-6fd3-48b1-9a1f-648f6368c09a", "name": "Sunset Pickleball"},
    {"id": "1925f835-e7cd-422b-bf9e-124dadf1a6aa", "name": "Sunset Tennis"},
    {"id": "73dc0950-4702-467d-ac49-792e7b2beab6", "name": "Sycamore Tennis"},
]

def parse_courts(html):
    """
    Parses the HTML response and extracts:
      - The selected facility ID (from the hidden input field)
      - All court data from buttons with class "booking-facility-list"
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get the selected facility id from the hidden input field
    selected_facility = soup.find('input', id='hdnSelectedFacilityId')
    selected_facility_id = selected_facility['value'] if selected_facility else None

    # Find all buttons representing courts
    court_buttons = soup.find_all('button', class_='booking-facility-list')
    courts = []
    for btn in court_buttons:
        button_id = btn.get('id')
        facility_id = btn.get('data-facility-id')
        court_name = btn.get('data-facility-name')
        if not court_name:
            # Fallback: get text from the first <span>
            span = btn.find('span')
            court_name = span.get_text(strip=True) if span else None
        courts.append({
            'button_id': button_id,
            'facility_id': facility_id,
            'court_name': court_name
        })
    
    return {
        'selected_facility_id': selected_facility_id,
        'courts': courts
    }

def get_facility_html(facility_id, aspnet_cookie):
    """
    Fetches the HTML for a given facility booking page using the ASP.NET Application Cookie.
    """
    url = f"https://secure.recreation.ucla.edu/booking/{facility_id}/facilities"
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
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    # Only the ASP.NET application cookie is provided.
    cookies = {".AspNet.ApplicationCookie": aspnet_cookie}
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch facility {facility_id}. Status code: {response.status_code}")
        return None

def main():
    # Replace with your actual ASP.NET Application Cookie value
    aspnet_cookie = "DkOd-NahgutVb9OM_hhTNP0kMyjl6oYAC9FWoZV25CUUn5C6QSC9uQEPhTcAGduHPm4NDBrFyHA4UgmwfHKvB23Tax1f0bd3umiajj5Zu8_xEXpWQ2Chz0x9Z4sDE7D1K1fVViodWkPPkeI-ITWFWVCKfoA_IgecF3mg42YVZXIt5016UJ-Lg4EbWQtZy5lFC_t8TU_WF06advD4Z9TWqAiTnQpXnLooSauAJ1nTHo86rt4oH-Pga1W9yk3jSb-oAWMZ5QPGE2fZUKpSWEpjPrRmgxKEkSSxOMhxWfz0Se0i_b6ucx_JJV8XXUlbECUE7u1dXIthEbqWDAkl4g0eB22uEifLBkR84WGba1M8cmtU2TDmuWPhDnzzJKP95JKv"
    
    for facility in REC_FACILITIES:
        print(f"Fetching data for {facility['name']} (ID: {facility['id']})")
        html = get_facility_html(facility["id"], aspnet_cookie)
        if html:
            data = parse_courts(html)
            print(f"Selected Facility ID in HTML: {data['selected_facility_id']}")
            print("Courts:")
            for court in data['courts']:
                print(f" - {court['court_name']} (Button ID: {court['button_id']}, Facility ID: {court['facility_id']})")
        print("-" * 40)

if __name__ == "__main__":
    main()
