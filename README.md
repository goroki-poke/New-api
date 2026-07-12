# E-Commerce Product Data API

Scrape product details, prices, and availability from major e-commerce sites. Returns clean structured JSON. Ideal for price comparison apps, shopping tools, and inventory tracking.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/v1/product?url=...` | Get product details by URL |
| GET | `/v1/search?q=...` | Search products by keyword |

### GET /v1/product

Scrape a product page and return structured data.

**Parameters:**
- `url` (required): Full product URL (e.g. `https://www.amazon.com/dp/B0XXXXX`)
- `site` (optional): Site identifier (`amazon`, default)
- `refresh` (optional): Set `true` to force re-scrape

**Response:**
```json
{
  "id": "amazon:B0XXXXX",
  "site": "amazon",
  "url": "https://www.amazon.com/dp/B0XXXXX",
  "title": "Product Name",
  "price": 29.99,
  "currency": "USD",
  "availability": "in_stock",
  "description": "Product description text...",
  "images": ["https://..."],
  "rating": 4.5,
  "review_count": 1234,
  "seller": "BrandName",
  "category": "Electronics",
  "scraped_at": "2026-07-09T12:00:00"
}
```

### GET /v1/search

Search products by keyword.

**Parameters:**
- `q` (required): Search keyword
- `site` (optional): Site identifier (`amazon`)
- `limit` (optional): Max results (1-50, default 10)

---

## Local Development

```bash
# 1. Install dependencies (already done in venv)
.\venv\Scripts\pip install -r requirements.txt

# 2. Copy and edit env
copy .env.example .env

# 3. Start PostgreSQL (or point to Supabase)
docker compose up -d db

# 4. Run the API
.\venv\Scripts\uvicorn app.main:app --reload --port 8000

# 5. Open docs
# http://localhost:8000/docs
```

## Deploy to VPS

### Option A: Docker

```bash
# Build and run with PostgreSQL
docker compose up -d

# Or build just the API (point to your own Postgres/Supabase)
docker build -t ecommerce-api .
docker run -d -p 8000:8000 --env-file .env ecommerce-api
```

### Option B: Direct (no Docker)

```bash
# Install deps
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Set up a reverse proxy (Caddy/Nginx) to handle SSL and domain:

```
# Caddyfile example
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

---

## RapidAPI Setup Guide

### Step 1: Deploy the API

Before listing on RapidAPI, your API must be publicly accessible.

1. Deploy to your VPS (see above)
2. Ensure it's accessible at `https://api.yourdomain.com`
3. Verify: `curl https://api.yourdomain.com/health` returns `{"status":"ok"}`

### Step 2: Create a RapidAPI Provider Account

1. Go to [rapidapi.com](https://rapidapi.com) and sign up as a provider
2. Click your profile → **Provider Dashboard**
3. Click **Add New API**

### Step 3: Configure Your API on RapidAPI

**Basic Info:**
- **Name:** E-Commerce Product Data API
- **Description:**
  > Scrape product details, prices, and availability from Amazon and other e-commerce sites. Get clean JSON with title, price, rating, images, seller info, and more. Perfect for price comparison apps, shopping assistants, and inventory tracking.
- **Category:** Data → E-Commerce
- **Logo:** Upload a 200x200px icon
- **Banner:** Upload a 1500x500px banner

**Endpoints Setup:**

For each endpoint, add:
- **Route:** `https://api.yourdomain.com/v1/product`
- **Method:** GET
- **Parameters:**
  - `url` (string, required) — "Full product URL to scrape (e.g. https://www.amazon.com/dp/B0XXXXX)"
  - `site` (string, optional, default: amazon) — "E-commerce site identifier"
  - `refresh` (boolean, optional, default: false) — "Force re-scrape instead of using cache"

For search endpoint:
- **Route:** `https://api.yourdomain.com/v1/search`
- **Method:** GET
- **Parameters:**
  - `q` (string, required) — "Search keyword (e.g. 'wireless headphones')"
  - `site` (string, optional, default: amazon) — "Site to search"
  - `limit` (integer, optional, default: 10) — "Max results"

**Endpoint descriptions are critical for conversion.** Be explicit:
- Bad: "Returns product data"
- Good: "Returns full product details including title, current price, availability status, high-res images, star rating, review count, seller/brand name, category, and description. Use this to populate product pages, price alerts, or shopping cart tools."

### Step 4: Generate Your Proxy Secret

1. In RapidAPI Provider Dashboard → **Security** tab
2. Click **Generate New Secret** under "Proxy Secret"
3. Copy the secret value

### Step 5: Set the Proxy Secret on Your Server

Add it to your `.env` file:

```
RAPIDAPI_PROXY_SECRET=your-generated-secret-here
```

This ensures only requests through RapidAPI reach your server. Direct requests are blocked with a 403 error.

### Step 6: Pricing Plans

Recommended pricing structure:

| Plan | Price | Requests/mo | Rate Limit |
|------|-------|-------------|------------|
| Free | $0 | 100 | 10/min |
| Basic | $19/mo | 5,000 | 60/min |
| Pro | $49/mo | 25,000 | 300/min |
| Ultra | $149/mo | 100,000 | 1000/min |

Copy the **Rate Limit** values into the RapidAPI plan configuration.

### Step 7: Test Before Publishing

1. Use RapidAPI's **Test Endpoint** feature in the dashboard
2. Make a test call to `GET /v1/product?url=https://www.amazon.com/dp/B0XXXXX`
3. Verify the response is clean JSON

### Step 8: Publish

1. Click **Save & Publish**
2. Your API is now live on the marketplace

### Step 9: Drive Traffic

1. **Write articles:** Publish a post like "How to build a price comparison tool with Python" linking to your API
2. **SEO:** Your RapidAPI listing page will be indexed by Google
3. **Community:** Share in relevant subreddits (r/webdev, r/entrepreneur) and dev.to

---

## Project Structure

```
ecommerce-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment config
│   ├── database.py          # SQLAlchemy async connection
│   ├── models.py            # Pydantic + ORM models
│   ├── cache.py             # In-memory TTL cache
│   ├── scrapers/
│   │   ├── base.py          # Abstract scraper base class
│   │   ├── amazon.py        # Amazon scraper
│   │   └── __init__.py      # Scraper registry
│   ├── routers/
│   │   ├── products.py      # Product endpoint
│   │   ├── search.py        # Search endpoint
│   │   └── health.py        # Health check
│   └── middleware/
│       ├── rapidapi.py      # RapidAPI proxy secret verification
│       └── rate_limit.py    # Per-plan rate limiting
├── scripts/
│   ├── schema.sql           # Raw SQL schema
│   └── init_db.py           # Create tables script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Adding More Sites

Create a new scraper in `app/scrapers/` following the `BaseScraper` interface:

```python
from app.scrapers.base import BaseScraper

class WalmartScraper(BaseScraper):
    SITE = "walmart"

    def product_id_from_url(self, url: str) -> str:
        ...

    async def scrape(self, url: str) -> Product:
        ...

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        ...
```

Then register it in `app/scrapers/__init__.py`:

```python
SCRAPERS = {
    "amazon": AmazonScraper(),
    "walmart": WalmartScraper(),
}
```
