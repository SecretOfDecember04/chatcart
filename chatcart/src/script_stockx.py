from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Set the correct path to your ChromeDriver
service = Service("/Users/longxuanlin/Downloads/chromedriver-mac-arm64/chromedriver")

# Start the browser
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the Dealmoon baoliao page
url = "https://www.dealmoon.com/baoliao"
driver.get(url)

# Wait a bit for the page to load fully
time.sleep(5)

# Scroll down to load more content if required
scroll_pause_time = 3
max_scroll_attempts = 10  # Scroll up to 10 times to load more content
last_height = driver.execute_script("return document.body.scrollHeight")

# Scroll down to load all content until no more new content loads or reach max_scroll_attempts
for _ in range(max_scroll_attempts):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Wait until the deal elements are loaded
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.box_item"))
    )
except Exception as e:
    print(f"Error while waiting for deal elements: {e}")
    driver.quit()
    exit()

# Extract data from all loaded deals
deals = driver.find_elements(By.CSS_SELECTOR, "div.box_item")
data = []

for deal in deals:  # Extract data from all deals that are currently loaded
    try:
        # Extract deal title (Product name)
        title_element = deal.find_element(By.CSS_SELECTOR, "span.text_wrap")
        title = title_element.text if title_element else "N/A"

        # Extract price(s)
        price_element = deal.find_element(By.CSS_SELECTOR, "span.deal_wrap")
        if price_element:
            # Check if there are children under price_element
            price_children = price_element.find_elements(By.XPATH, "./*")
            if len(price_children) == 0:
                # Only one price available
                price = price_element.text.strip()
            elif len(price_children) == 1:
                # One child, usually the discounted price
                price = price_children[0].text.strip()
            elif len(price_children) == 2:
                # Two children, typically both discounted and original price
                price = f"{price_children[0].text.strip()} (Original: {price_children[1].text.strip()})"
            else:
                price = "N/A"
        else:
            price = "N/A"

        # Add extracted data to the list
        data.append([title, price])
        print(f"Title: {title}, Price: {price}")

    except Exception as e:
        print(f"Error parsing a deal card: {e}")

# Close the browser
driver.quit()

# Writing data to CSV file
if data:
    with open('dealmoon_deals.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Deal Title', 'Price'])
        writer.writerows(data)

    print("Data successfully written to dealmoon_deals.csv")
else:
    print("No data found.")
