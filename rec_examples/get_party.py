import requests
import re

# Define the target URL
url = "https://secure.recreation.ucla.edu/profile"

# Replace with your actual `.AspNet.ApplicationCookie` value
cookies = {
    ".AspNet.ApplicationCookie": "5WOVZiC5g595rbsgmAOxfqbLD0ATdag_mELH8VQXp8eqms58E6_mx-pwmKe9vbaPYlmh9eCqkavi2okJnlSnaUWCfX50pbZFaEnGyHlGsBh4x1pOw_ltIA4dZfBTyyq0GXWzBQH6-IQcwxXL7xT8TwGU_AF8UATsJHdHrcxbaTpG4RWSJcfKR4IXQTZVnOtzg7rNia357hy2xfW7Dlkp5AZj0PsKXv2Km47DJFh0_Reyvb2D182Kf9YDKBm2ah8GMv_Oo2uDtPlABHyYuHEMPvSkMDrvrZxEtNfTtQtuj2UOwrdnGGj3TjJF1Gg_EIYHAW40SNR-7hMV-Ro181daMDBuA5nkUsWaFKP4R8bsxPQK59LfaamvgqtzLRKZe0jL"
}

# Make the request to the profile page
response = requests.get(url, cookies=cookies)

# Check if request was successful
if response.status_code == 200:
    html_content = response.text

    # Refined regex to match the hidden input field with PartyId
    match = re.search(r'<input[^>]+id="profileUserId"[^>]+value="([a-f0-9\-]+)"', html_content)

    if match:
        party_id = match.group(1)
        print(f"Extracted partyId: {party_id}")
    else:
        print("partyId not found in the response.")
else:
    print(f"Failed to fetch profile page. Status code: {response.status_code}")