CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(64) PRIMARY KEY,
    site VARCHAR(32) NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    currency VARCHAR(8) DEFAULT 'USD',
    availability VARCHAR(32) DEFAULT 'in_stock',
    description TEXT,
    images TEXT DEFAULT '[]',
    rating DOUBLE PRECISION,
    review_count INTEGER,
    seller VARCHAR(256),
    category VARCHAR(256),
    scraped_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_site ON products(site);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
