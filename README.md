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
