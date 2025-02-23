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
    "https://calendar.library.ucla.edu/spaces?lid=5567&gid=0&c=0",
    "https://calendar.library.ucla.edu/spaces?lid=4361&gid=0&c=0",
    "https://calendar.library.ucla.edu/spaces?lid=4752&gid=0&c=0",
    "https://calendar.library.ucla.edu/spaces?lid=6578&gid=0&c=0",
    "https://calendar.library.ucla.edu/spaces?lid=8312&gid=0&c=0",
    "https://calendar.library.ucla.edu/spaces?lid=19391&gid=0&c=0",
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
