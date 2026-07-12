import json
import re
from typing import Optional
from urllib.parse import quote_plus

from parsel import Selector

from app.models import Product
from app.scrapers.base import BaseScraper


class AmazonScraper(BaseScraper):
    SITE = "amazon"

    def product_id_from_url(self, url: str) -> str:
        match = re.search(r"/(?:dp|product)/([A-Z0-9]{10})(?:[/?]|$)", url, re.IGNORECASE)
        if match:
            return f"amazon:{match.group(1)}"
        raise ValueError(f"Could not extract Amazon product ID from URL: {url}")

    def _parse_json_ld(self, html: str) -> Optional[dict]:
        selectors = Selector(text=html)
        for script in selectors.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    return data
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
            except (json.JSONDecodeError, KeyError):
                continue
        return None

    def _parse_from_html(self, html: str, url: str) -> dict:
        sel = Selector(text=html)
        result = {}

        title = sel.css("#productTitle::text").get("").strip()
        if not title:
            title = sel.css("h1 span.a-size-large::text").get("").strip()
        result["title"] = title

        price_str = (
            sel.css(".a-price .a-offscreen::text").get("")
            or sel.css("#price_inside_buybox::text").get("")
            or sel.css(".a-price-whole::text").get("")
        )
        price_str = re.sub(r"[^0-9.,]", "", price_str).strip()
        try:
            result["price"] = float(price_str.replace(",", "")) if price_str else 0.0
        except ValueError:
            result["price"] = 0.0

        rating_str = sel.css("span.a-icon-alt::text").get("")
        if rating_str:
            match = re.search(r"([\d.]+)\s*out\s*of\s*5", rating_str, re.IGNORECASE)
            result["rating"] = float(match.group(1)) if match else None
        else:
            result["rating"] = None

        review_str = sel.css("#acrCustomerReviewText::text").get("")
        if review_str:
            match = re.search(r"([\d,]+)", review_str.replace(",", ""))
            result["review_count"] = int(match.group(1)) if match else None
        else:
            result["review_count"] = None

        images = sel.css("#landingImage::attr(src)").getall()
        if not images:
            images = sel.css("img.a-dynamic-image::attr(data-old-hires)").getall()
        if not images:
            images = sel.css("div.imgTagWrapper img::attr(src)").getall()
        result["images"] = images[:5]

        seller = sel.css("#sellerProfileTriggerId::text, .a-spacing-small .a-size-small::text").get("")
        result["seller"] = seller.strip() if seller else None

        breadcrumbs = sel.css("#wayfinding-breadcrumbs_container a::text, "
                               "#breadcrumb-back-link+span .a-list-item a::text").getall()
        result["category"] = breadcrumbs[-1].strip() if breadcrumbs else None

        desc = sel.css("#productDescription p::text").get("")
        if not desc:
            desc = sel.css("#feature-bullets li span::text").get("")
        result["description"] = desc.strip() if desc else None

        return result

    async def scrape(self, url: str) -> Product:
        product_id = self.product_id_from_url(url)
        client = await self.get_client()
        resp = await client.get(url)
        resp.raise_for_status()
        html = resp.text

        ld = self._parse_json_ld(html)
        html_data = self._parse_from_html(html, url)

        if ld:
            offers = ld.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}

            price = None
            if isinstance(offers, dict):
                try:
                    price = float(offers.get("price", 0))
                except (ValueError, TypeError):
                    price = html_data.get("price", 0.0)
            else:
                price = html_data.get("price", 0.0)

            images = ld.get("image", [])
            if isinstance(images, str):
                images = [images]
            elif isinstance(images, dict):
                images = [images.get("url", "")]

            return Product(
                id=product_id,
                site=self.SITE,
                url=url,
                title=ld.get("name", html_data.get("title", "")),
                price=price or html_data.get("price", 0.0),
                currency=offers.get("priceCurrency", "USD") if isinstance(offers, dict) else "USD",
                availability=self._normalize_availability(
                    offers.get("availability", "") if isinstance(offers, dict) else ""
                ),
                description=ld.get("description", html_data.get("description")),
                images=images or html_data.get("images", []),
                rating=ld.get("aggregateRating", {}).get("ratingValue") if isinstance(ld.get("aggregateRating"), dict) else html_data.get("rating"),
                review_count=ld.get("aggregateRating", {}).get("reviewCount") if isinstance(ld.get("aggregateRating"), dict) else html_data.get("review_count"),
                seller=ld.get("brand", {}).get("name") if isinstance(ld.get("brand"), dict) else html_data.get("seller"),
                category=html_data.get("category"),
                scraped_at=__import__("datetime").datetime.utcnow(),
            )

        return Product(
            id=product_id,
            site=self.SITE,
            url=url,
            title=html_data.get("title", ""),
            price=html_data.get("price", 0.0),
            currency="USD",
            availability="in_stock" if html_data.get("price", 0) > 0 else "unknown",
            description=html_data.get("description"),
            images=html_data.get("images", []),
            rating=html_data.get("rating"),
            review_count=html_data.get("review_count"),
            seller=html_data.get("seller"),
            category=html_data.get("category"),
            scraped_at=__import__("datetime").datetime.utcnow(),
        )

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        search_url = f"https://www.amazon.com/s?k={quote_plus(query)}"
        client = await self.get_client()
        resp = await client.get(search_url)
        resp.raise_for_status()
        sel = Selector(text=resp.text)

        products = []
        results = sel.css("[data-asin][data-component-type='s-search-result']")[:limit]

        for item in results:
            asin = item.attrib.get("data-asin", "")
            if not asin or asin == "":
                continue

            title_el = item.css("h2 a span::text").get("")
            price_whole = item.css(".a-price-whole::text").get("")
            price_frac = item.css(".a-price-fraction::text").get("")
            image = item.css("img.s-image::attr(src)").get("")
            rating = item.css("span.a-icon-alt::text").get("")

            price_str = f"{price_whole or '0'}.{price_frac or '0'}"
            try:
                price = float(price_str.replace(",", ""))
            except ValueError:
                price = 0.0

            rating_val = None
            if rating:
                match = re.search(r"([\d.]+)\s*out\s*of\s*5", rating, re.IGNORECASE)
                if match:
                    rating_val = float(match.group(1))

            product_url = f"https://www.amazon.com/dp/{asin}"

            products.append(Product(
                id=f"amazon:{asin}",
                site=self.SITE,
                url=product_url,
                title=title_el.strip(),
                price=price,
                currency="USD",
                availability="in_stock" if price > 0 else "unknown",
                images=[image] if image else [],
                rating=rating_val,
                scraped_at=__import__("datetime").datetime.utcnow(),
            ))

        return products

    def _normalize_availability(self, avail: str) -> str:
        if not avail:
            return "unknown"
        if "in stock" in avail.lower():
            return "in_stock"
        if "backorder" in avail.lower():
            return "backorder"
        if "preorder" in avail.lower():
            return "preorder"
        if "sold" in avail.lower() or "out of" in avail.lower():
            return "out_of_stock"
        if "instock" in avail.lower() or "in stock" in avail.lower():
            return "in_stock"
        return "unknown"
