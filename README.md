# Best Buy Price Scraper with Supabase

## Setup Instructions

### 1. Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL in `supabase_setup.sql` in your Supabase SQL Editor
3. Get your Supabase credentials:
   - **URL**: Found in Settings → API → Project URL
   - **Anon Key**: Found in Settings → API → Project API keys → anon/public

### 2. GitHub Secrets Setup

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key

### 3. Local Development

Create a `.env` file in the project root (don't commit this):

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

Then install dependencies and run:

```bash
pip install -r requirements.txt
python scrape_bestbuy.py
```

### 4. Database Schema

The `price_history` table stores:
- `id`: Unique identifier
- `item_name`: Product name searched
- `product_url`: Best Buy product URL
- `price`: Extracted price
- `scraped_at`: When the data was scraped
- `created_at`: Database timestamp

### 5. Querying Your Data

In Supabase, you can query price history:

```sql
-- Get latest prices for all products
SELECT DISTINCT ON (item_name) 
    item_name, price, scraped_at
FROM price_history
ORDER BY item_name, scraped_at DESC;

-- Track price changes over time
SELECT item_name, price, scraped_at
FROM price_history
WHERE item_name = 'Apple - iPhone 17 Pro Max 256GB - Silver (AT&T)'
ORDER BY scraped_at DESC;

-- Get all records from the last 24 hours
SELECT * FROM price_history
WHERE scraped_at > NOW() - INTERVAL '24 hours'
ORDER BY scraped_at DESC;
```
