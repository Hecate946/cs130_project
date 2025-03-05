import requests
from bs4 import BeautifulSoup

def get_slots_html(facility_id, court_slot_id, y, m, d, aspnet_cookie):
    """
    Makes a GET request to the booking slots URL for a given facility/court_slot on a specific date.
    """
    url = f"https://secure.recreation.ucla.edu/booking/{facility_id}/slots/{court_slot_id}/{y}/{m}/{d}"
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
    cookies = {".AspNet.ApplicationCookie": aspnet_cookie}
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch slots for facility {facility_id}, slot {court_slot_id} on {y}-{m}-{d}. Status code: {response.status_code}")
        return None

def parse_slot_availability(html, y="2025", m="2", d="27", t="", v="0"):
    """
    Parses the booking slots HTML and extracts data for each time slot.
    Each slot dictionary includes:
      - "slot_number": from data-slot-number attribute.
      - "participant": a nested dictionary containing:
            "id": the data-participant-id,
            "aid": (from the button's data-apt-id, if available),
            "tsid": (from the button's data-timeslot-id, if available),
            "tsild": (from the button's data-timeslotinstance-id, if available)
      - "availability": either "booked", "unavailable", "available", or "opens"
      - "opening_time": if the slot is not booked/unavailable/available but shows an opening message.
      - "time": the time string extracted from the <strong> element.
      - "spots_info": if any element (outside the button container) indicates available spots.
      - Additional parameters: y, m, d, t, v.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    slot_items = soup.find_all('div', class_='booking-slot-item')
    slots = []
    for item in slot_items:
        slot = {}
        slot["slot_number"] = item.get("data-slot-number")
        
        # Participant info from container
        participant_id = item.get("data-participant-id")
        
        # Default extra attributes from button (if available)
        aid = tsid = tsild = None
        
        # Check the right-side container for booking actions.
        btn_container = item.find('div', class_='booking-slot-item-right')
        availability = "unknown"
        opening_time = None
        if btn_container:
            # Look for a button first.
            button = btn_container.find('button')
            if button:
                # Attempt to extract additional attributes from the button.
                aid = button.get("data-apt-id")
                tsid = button.get("data-timeslot-id")
                tsild = button.get("data-timeslotinstance-id")
                btn_text = button.get_text(strip=True)
                if "Booked" in btn_text:
                    availability = "booked"
                elif "Unavailable" in btn_text:
                    availability = "unavailable"
                else:
                    availability = "available"
            else:
                # No button found; try to see if there is a span indicating opening time.
                span = btn_container.find('span')
                if span and "Opens at" in span.get_text():
                    opening_time = span.get_text(strip=True)
                    availability = "opens"
                else:
                    availability = "unknown"
        else:
            availability = "unknown"
        
        # Nest participant information.
        slot["participant"] = {
            "id": participant_id,
            "aid": aid,
            "tsid": tsid,
            "tsild": tsild
        }
        
        slot["availability"] = availability
        
        if opening_time:
            slot["opening_time"] = opening_time
        
        # Extract the time from the <strong> element inside a <p> tag.
        strong_elem = item.find('strong')
        slot["time"] = strong_elem.get_text(strip=True) if strong_elem else None
        
        # Look for an element that indicates spots available.
        # For example, a <span> that contains "spot" in its text.
        spots_elem = item.find(lambda tag: tag.name == "span" and tag.get_text(strip=True).lower().find("spot") != -1)
        if spots_elem:
            slot["spots_info"] = spots_elem.get_text(strip=True)
        else:
            slot["spots_info"] = None
        
        # Additional parameters.
        slot["y"] = y
        slot["m"] = m
        slot["d"] = d
        slot["t"] = t
        slot["v"] = v
        
        slots.append(slot)
    
    return slots

def main():
    # Replace with your actual ASP.NET Application Cookie value.
    aspnet_cookie = "DmtCmQwSfmeE3hxjpzPcmGd3wWHVw9H07P9bkvhfdiTmi04HMwEIIkERrb0TWCXLzEVvZwVkVV5s7-fjwwLr9f3M9svqA1dUDqzc-6smrINJxV97GPk1AQwH3v1Qfo9LRUMxJAynNRePorSQdt5Kn6bbw2qHxYviNgCU4WTOc-HGRebhITNGoR4nI_ox_1LZOUUX7WnfsSo9b013ICr8N0TLuLcmF5XS2gD0_9wE_I73q9r3U-6IXJETXCFVX7gQFtEbf4J5XzvjaUlR6xJd_4Di-F-Qhb3CR9excTQ8hEJpNNkh25KipXAx3nyQio_ItlrPAEcNhgQPkGgiLCppoxqEw3thIYIeZaSdzZT-GS-u-i_XzGtGpejEr3oiC6vc"

    # Predefined parameters for demonstration.
    facility_id = "02a10035-6fd3-48b1-9a1f-648f6368c09a"  # For example: Sunset Pickleball facility id.
    court_slot_id = "37aa52d3-7c1f-4969-954c-a861454e85ea"   # Example: a court slot id (from booking response).
    
    # Date parameters.
    year = "2025"
    month = "3"
    day = "4"
    t_param = ""
    v_param = "0"
    
    html = get_slots_html(facility_id, court_slot_id, year, month, day, aspnet_cookie)
    if html:
        slots = parse_slot_availability(html, y=year, m=month, d=day, t=t_param, v=v_param)
        for slot in slots:
            print(slot)
    else:
        print("No HTML returned; cannot parse slots.")

if __name__ == "__main__":
    main()
