from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode (no browser UI)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Use ChromeDriverManager to automatically manage and install ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Load the webpage
driver.get('https://www.goat.com/sneakers')

# Wait for the sneaker grid to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'GridCellProductInfo__Name-sc-17lfnu8-3'))
    )
except:
    print("Sneaker grid did not load.")
    driver.quit()

# Scroll the page to load more items
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_count = 0
max_scrolls = 50  # Increase this to load more items (adjust based on performance and page load speed)

while scroll_count < max_scrolls:
    scroll_count += 1

    # Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for new content to load
    time.sleep(5)  # Increase delay to allow more items to load

    # Check if the page height has changed (i.e., new content has loaded)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        print("No more new content to load.")
        break  # No more content to load
    last_height = new_height

# Get the page source after scrolling
page_source = driver.page_source

# Parse the page with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find the sneaker items based on 'data-qa' attribute
sneakers = soup.find_all('div', {'data-qa': 'grid_cell_product_name'})

# Prepare lists to store data
sneaker_types = []
sneaker_prices = []

# Loop through all the sneakers found
for sneaker in sneakers:
    # Extract the type (name of the sneaker) from the div's text
    sneaker_type = sneaker.text.strip() if sneaker else 'N/A'

    # Find the corresponding price for each sneaker
    price_tag = sneaker.find_next('span', class_='LocalizedCurrency__Amount-sc-yoa0om-0')
    price = price_tag.text.strip() if price_tag else 'N/A'

    # Append the extracted data to the lists
    sneaker_types.append(sneaker_type)
    sneaker_prices.append(price)

# Close the browser
driver.quit()

# Create a Pandas DataFrame to hold the scraped data
df = pd.DataFrame({
    'Sneaker Type': sneaker_types,
    'Price': sneaker_prices,
})

# Save the data to an Excel file
df.to_excel('sneaker_data.xlsx', index=False)

print(f"Data has been saved to 'sneaker_data.xlsx'. Total sneakers: {len(sneaker_types)}")
