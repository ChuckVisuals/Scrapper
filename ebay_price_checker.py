import requests
from urllib.parse import quote_plus
import re
import os
from supabase_client import init_supabase
from items import ITEMS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://www.ebay.com/sch/i.html?_nkw={item_name}&LH_ItemCondition=3&LH_BIN=1&rt=nc&LH_Sold=1"


def find_product_avg_ebay(item_name: str, timeout: float = 30.0) -> float:
    """Search for an item and return the first product link using OCR."""
    search_url = f"{BASE_URL.format(item_name=quote_plus(item_name))}"

    # Set up Selenium headless browser with stealth options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # New headless mode (less detectable)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation flag
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(search_url)

    # Wait for at least one price span to appear (up to 15 seconds)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.su-styled-text.positive.bold.large-1.s-card__price")
            )
        )
    except Exception as e:
        print("Timeout waiting for price elements:", e)

    html = driver.page_source

    # Strict regex: match only the exact class attribute for the price span
    price_pattern = r'<span class="su-styled-text positive bold large-1 s-card__price">\s*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*</span>'
    matches = re.findall(price_pattern, html)
    print(matches)
    first_3_prices = matches[:3]
    print("First 3 prices:", first_3_prices)
    driver.quit()

    # Convert price strings to floats
    prices = []
    for price_str in first_3_prices:
        price_num = float(price_str.replace("$", "").replace(",", ""))
        prices.append(price_num)

    avg_price = sum(prices) / len(prices) if prices else 0.0
    print(f"Average of first 3 prices: {avg_price}")
    return avg_price
    



if __name__ == "__main__":
    # Initialize Supabase client
    supabase = init_supabase()
    
    for item in ITEMS:
        avg = find_product_avg_ebay(item)