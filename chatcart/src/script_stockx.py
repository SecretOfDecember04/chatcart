from playwright.sync_api import sync_playwright
import csv

# Path to save the CSV file
csv_file_path = 'dealmoon_deals.csv'

# List to store the extracted data
data = []

# Using Playwright to render JavaScript content and scrape the data
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Set up headers to make the request look more like a regular browser
    page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    })

    try:
        # Go to the Dealmoon deals page
        page.goto("https://www.dealmoon.com/baoliao", timeout=60000)

        # Wait for the content to load
        page.wait_for_selector('div.box_item', timeout=60000)

        # Extract deals from the page
        deals = page.query_selector_all('div.box_item')
        for deal in deals:
            title_element = deal.query_selector('span.text_wrap')
            price_element = deal.query_selector('span.deal_wrap')

            title = title_element.inner_text() if title_element else "N/A"
            price = price_element.inner_text() if price_element else "N/A"

            data.append([title, price])

    except Exception as e:
        print(f"Error occurred: {e}")

    # Close the browser
    browser.close()

# Write the data to a CSV file
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Price'])
    writer.writerows(data)

print(f"Data successfully written to {csv_file_path}")
