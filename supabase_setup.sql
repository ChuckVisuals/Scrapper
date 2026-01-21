-- Create the price_history table in Supabase
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    item_name TEXT NOT NULL,
    product_url TEXT NOT NULL,
    price TEXT NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create an index on scraped_at for faster queries
CREATE INDEX IF NOT EXISTS idx_price_history_scraped_at ON price_history(scraped_at DESC);

-- Create an index on item_name for filtering by product
CREATE INDEX IF NOT EXISTS idx_price_history_item_name ON price_history(item_name);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow inserts (adjust based on your auth setup)
CREATE POLICY "Allow anonymous inserts" ON price_history
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy to allow reads (adjust based on your auth setup)
CREATE POLICY "Allow public reads" ON price_history
    FOR SELECT
    TO anon
    USING (true);
