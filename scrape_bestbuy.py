import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import os
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from items import ITEMS

BASE_URL = "https://www.bestbuy.com/site/searchpage.jsp?id=pcat17071&st="
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
}


def find_product_link(item_name: str, timeout: float = 30.0) -> str:
    """Search for an item and return the first product link."""
    search_url = f"{BASE_URL}{quote_plus(item_name)}"
    resp = requests.get(search_url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find the first product item (using actual class from HTML)
    product = soup.select_one("li.product-list-item")
    if not product:
        return None
    
    # Find the product link (based on actual HTML structure: a.product-list-item-link)
    link = product.select_one("a.product-list-item-link")
    if not link or not link.get("href"):
        return None
    
    href = link["href"]
    # Best Buy returns full URLs in their search results
    return href

def get_price_from_link(link: str, timeout: float = 30.0) -> str:
    """Fetch the product page and extract the price."""
    resp = requests.get(link, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    
    soup = BeautifulSoup(resp.text, "html.parser")
    import json
    
    # Strategy 1: Look for price data in embedded JSON (Best Buy uses Apollo/GraphQL state)
    # Search for script tags containing price data
    for script in soup.find_all("script"):
        script_text = script.string
        if script_text and "customerPrice" in script_text:
            # Try to extract JSON containing price info
            try:
                # Look for price data in Apollo state transport
                if "ApolloSSRDataTransport" in script_text or "customerPrice" in script_text:
                    # Extract prices using regex from the JSON data
                    one_time_prices = re.findall(r'"customerPrice":(\d+(?:\.\d{2})?)', script_text)
                    if one_time_prices:
                        # Return the first valid price found (usually the main one-time price)
                        price_value = one_time_prices[0]
                        return f"${price_value}"
            except:
                pass
    
    # Strategy 2: Look for standard customer price (one-time purchase price for non-carrier items)
    # Try both "customer-price" and "price-block-customer-price"
    price_elem = (soup.find("span", {"data-testid": "customer-price"}) or 
                  soup.find("span", {"data-testid": "price-block-customer-price"}) or
                  soup.find("div", {"data-testid": "price-block"}))
    
    if price_elem:
        text = price_elem.get_text(strip=True)
        match = re.search(r'\$\d+(?:,\d{3})?(?:\.\d{2})?', text)
        if match:
            return match.group(0)
    
    # Strategy 3: Fallback to monthly payment price if no one-time price found
    for span in soup.find_all("span", {"data-testid": "message-parts-text"}):
        text = span.get_text(strip=True)
        match = re.search(r'\$\d+\.\d{2}/mo\.?', text)
        if match:
            return match.group(0)
    
    return "Price not found"


TIMEOUT = 30.0

def init_supabase() -> Client:
    """Initialize Supabase client."""
    # Load .env if present for local development
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    print(f"Supabase URL: {url}")
    print(f"Supabase Key: {'SET' if key else 'NOT SET'}")
    
    if not url or not key:
        print("WARNING: SUPABASE_URL or SUPABASE_KEY not set. Data will not be uploaded.")
        return None
    
    return create_client(url, key)

def upload_to_supabase(supabase: Client, item_name: str, link: str, price: str):
    """Upload scraped data to Supabase."""
    if not supabase:
        return
    
    try:
        data = {
            "item_name": item_name,
            "product_url": link,
            "price": price,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("price_history").insert(data).execute()
        print(f"✓ Uploaded to Supabase")
    except Exception as e:
        print(f"✗ Failed to upload to Supabase: {e}")

if __name__ == "__main__":
    # Initialize Google Sheets
    # sheets_service, sheet_id = init_google_sheets()
    
    # Initialize Supabase client
    supabase = init_supabase()
    
    for item in ITEMS:
        print(f"Searching: {item}")
        link = find_product_link(item, timeout=TIMEOUT)
        if link:
            print(f"Found: {link}")
            price = get_price_from_link(link, timeout=TIMEOUT)
            if price:
                print(f"Price: {price}")
                #save_to_google_sheets(sheets_service, sheet_id, item, link, price)
                upload_to_supabase(supabase, item, link, price)
            else:
                print("Price not found")
        else:
            print("Not found")
        print()
        print()



