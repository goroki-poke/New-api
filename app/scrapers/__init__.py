from app.scrapers.amazon import AmazonScraper

SCRAPERS = {
    "amazon": AmazonScraper(),
}


def get_scraper(site: str):
    scraper = SCRAPERS.get(site.lower())
    if not scraper:
        raise ValueError(f"Unsupported site: {site}. Supported: {list(SCRAPERS.keys())}")
    return scraper
