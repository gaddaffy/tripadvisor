import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up ChromeDriver
driver_path = "./chromedriver"  # enter chromedriver path in this line though it is advisable to keep path same as python file
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# chrome web browser opens web to get URLs representative of the cities displayed
city_url = "https://www.tripadvisor.co.uk/Restaurants-g186216-United_Kingdom.html"
driver.get(city_url)

# Locate the element with XPath by inspecting the element on the chromebrowser
element = driver.find_element(By.XPATH, "//div[@class='geos_grid']")

# Find all "a" elements inside the element representing our texts of interest
a_elements = element.find_elements(By.TAG_NAME, "a")

# Create a list to store city data
city_data = []

# Get the text attribute and exclude "Restaurants"
for a in a_elements:
    text = a.text.strip()
    if "Restaurants" in text:
        text = text.replace("Restaurants", "").strip()
        city_url = a.get_attribute("href")
        city_data.append({"City": text, "City URL": city_url})

# Similarly, initialize an empty list to store restaurant data
restaurant_data = []

# Loop through each city
for city in city_data:
    city_name = city["City"]
    city_url = city["City URL"]

    # Load the website to get restaurant URLs
    driver.get(city_url)

    # Wait for 5 seconds to allow page features load
    time.sleep(5)

    # Select the checkbox with the specified XPath and value. "Cheap Eats" may be replaced with similar filter texts on the site

    input_checkbox = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//span[@class='mTKbF'][normalize-space()='Cheap Eats']")))
    driver.execute_script("arguments[0].click();", input_checkbox)

    # Wait for 5 seconds to allow page load features
    time.sleep(5)

    # Get the current URL after applying filters
    filtered_city_url = driver.current_url

    # Scrape the text inside the elements on the current page
    text_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'RfBGI')]")
    for element in text_elements:
        restaurant_url = element.find_element(By.TAG_NAME, "a").get_attribute("href")
        restaurant_name = element.text
        if not restaurant_name.startswith(("Ecco Pizza", "Moyos Burgers", "Sausage Shack R")) and "." in restaurant_name:
            restaurant_name = restaurant_name.split(".", 1)[1].strip()
            restaurant_data.append({"City": city_name, "Restaurant": restaurant_name, "Restaurant URL": restaurant_url})

    # Loop to navigate through multiple pages
    while True:
        try:
            # Click the "Next" button
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Next']")))
            driver.execute_script("arguments[0].click();", next_button)

            # Wait for 5 seconds
            time.sleep(5)

            # Get the current URL after navigating to the next page
            next_page_url = driver.current_url

            # Scrape the text inside the elements on the current page
            text_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'RfBGI')]")
            for element in text_elements:
                restaurant_url = element.find_element(By.TAG_NAME, "a").get_attribute("href")
                restaurant_name = element.text
                if not restaurant_name.startswith(("Ecco Pizza", "Moyos Burgers", "Sausage Shack R")) and "." in restaurant_name:
                    restaurant_name = restaurant_name.split(".", 1)[1].strip()
                    restaurant_data.append({"City": city_name, "Restaurant": restaurant_name, "Restaurant URL": restaurant_url})

        except:
            # Stop the loop when the last page is reached or an exception occurs
            break

# Close the browser
driver.quit()

# Create a DataFrame for restaurant data
restaurant_df = pd.DataFrame(restaurant_data)

# Save the data as a CSV file with only city and Restaurant as output columns
restaurant_df.to_csv('final.csv', index=False, columns=["City", "Restaurant"])
