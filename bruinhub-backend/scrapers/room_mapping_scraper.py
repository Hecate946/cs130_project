from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# Set up WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background
driver = webdriver.Chrome(options=options)

# Open the page
urls = [
    "https://calendar.library.ucla.edu/reserve/spaces/powell",
    "https://calendar.library.ucla.edu/reserve/spaces/yrl",
    "https://calendar.library.ucla.edu/reserve/spaces/musickits",
    "https://calendar.library.ucla.edu/spaces?lid=6578",
    "https://calendar.library.ucla.edu/reserve/spaces/SEL",
    "https://calendar.library.ucla.edu/spaces?lid=19391",
]

for url in urls:
    driver.get(url)

    # Wait for JavaScript to load
    time.sleep(1)

    # Extract JavaScript variable (resources)
    script_data = driver.execute_script("return resources;")

    # Process the data
    room_data = [{"name": room["title"], "id": room["eid"]}
                 for room in script_data]

    # Print results
    for room in room_data:
        print(f"{room['id']}: \"{room['name']}\"")

# Close WebDriver
driver.quit()
