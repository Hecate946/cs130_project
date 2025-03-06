import requests

def reserve_court(bId, fId, aId, tsId, tsiId, y, m, d, t, v, aspnet_cookie):
    """
    Reserve a court by sending a POST request to the UCLA Recreation reserve endpoint.
    
    Parameters:
      - bId: Booking facility id (e.g. "02a10035-6fd3-48b1-9a1f-648f6368c09a")
      - fId: Facility (court slot) id (e.g. "37aa52d3-7c1f-4969-954c-a861454e85ea")
      - aId: Appointment id (data-apt-id from the booking response)
      - tsId: Time slot id (data-timeslot-id from the booking response)
      - tsiId: Time slot instance id (data-timeslotinstance-id from the booking response)
      - y: Year (e.g. "2025")
      - m: Month (e.g. "3")
      - d: Day (e.g. "4")
      - t: t parameter (empty string if not needed)
      - v: v parameter (e.g. "0")
      - aspnet_cookie: Your .AspNet.ApplicationCookie value for authentication
      
    Returns:
      - The response object from the POST request.
    """
    url = "https://secure.recreation.ucla.edu/booking/reserve"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://secure.recreation.ucla.edu",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0"
    }
    cookies = {".AspNet.ApplicationCookie": aspnet_cookie}
    data = {
        "bId": bId,
        "fId": fId,
        "aId": aId,
        "tsId": tsId,
        "tsiId": tsiId,
        "y": y,
        "m": m,
        "d": d,
        "t": t,
        "v": v
    }
    
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    return response

def main():
    # Replace with your actual ASP.NET Application Cookie value.
    aspnet_cookie = "YOUR_COOKIE_HERE"
    
    # Example parameters based on the provided curl
    bId = "02a10035-6fd3-48b1-9a1f-648f6368c09a"          # Facility id (e.g., Sunset Pickleball)
    fId = "37aa52d3-7c1f-4969-954c-a861454e85ea"           # Court slot id
    aId = "7cb0503f-9912-469e-b5e2-acfd9d2b313a"           # Appointment id (data-apt-id)
    tsId = "8dcb85c3-9bb1-43c3-80b1-a6f10c173b32"           # Time slot id (data-timeslot-id)
    tsiId = "fb18a690-1a74-40fb-9769-d85ff73f0a40"          # Time slot instance id (data-timeslotinstance-id)
    y = "2025"
    m = "3"
    d = "4"
    t = ""
    v = "0"
    
    # Make the reservation request
    response = reserve_court(bId, fId, aId, tsId, tsiId, y, m, d, t, v, aspnet_cookie)
    
    # Print response details
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

if __name__ == "__main__":
    main()
