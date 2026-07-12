import json
import hashlib
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.database import async_session
from app.models import Product, ProductORM, ErrorResponse
from app.scrapers import get_scraper
from app.cache import product_cache

router = APIRouter(prefix="/v1", tags=["products"])


def _orm_to_product(p: ProductORM) -> Product:
    images = []
    try:
        images = json.loads(p.images) if isinstance(p.images, str) else (p.images or [])
    except (json.JSONDecodeError, TypeError):
        images = []
    return Product(
        id=p.id,
        site=p.site,
        url=p.url,
        title=p.title,
        price=p.price,
        currency=p.currency,
        availability=p.availability,
        description=p.description,
        images=images,
        rating=p.rating,
        review_count=p.review_count,
        seller=p.seller,
        category=p.category,
        scraped_at=p.scraped_at,
    )


@router.get(
    "/product",
    response_model=Product,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    summary="Get product details by URL",
    description="Scrapes product data from an e-commerce URL. Returns title, price, availability, images, rating, and more.",
)
async def get_product(
    url: str = Query(..., description="Full product URL (e.g. https://www.amazon.com/dp/B0XXXXX)"),
    site: str = Query("amazon", description="E-commerce site identifier"),
    refresh: bool = Query(False, description="Force re-scrape instead of using cache"),
):
    scraper = get_scraper(site)

    try:
        product_id = scraper.product_id_from_url(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cache_key = f"product:{product_id}"

    if not refresh:
        cached = product_cache.get(cache_key)
        if cached:
            return cached

        async with async_session() as session:
            result = await session.execute(
                select(ProductORM).where(ProductORM.id == product_id)
            )
            db_product = result.scalar_one_or_none()
            if db_product:
                product = _orm_to_product(db_product)
                product_cache.set(cache_key, product)
                return product

    try:
        product = await scraper.scrape(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to scrape product: {str(e)}")

    product_cache.set(cache_key, product)

    try:
        async with async_session() as session:
            existing = await session.get(ProductORM, product_id)
            if existing:
                existing.title = product.title
                existing.price = product.price
                existing.currency = product.currency
                existing.availability = product.availability
                existing.description = product.description
                existing.images = json.dumps(product.images)
                existing.rating = product.rating
                existing.review_count = product.review_count
                existing.seller = product.seller
                existing.category = product.category
                existing.updated_at = datetime.utcnow()
            else:
                session.add(ProductORM(
                    id=product.id,
                    site=product.site,
                    url=product.url,
                    title=product.title,
                    price=product.price,
                    currency=product.currency,
                    availability=product.availability,
                    description=product.description,
                    images=json.dumps(product.images),
                    rating=product.rating,
                    review_count=product.review_count,
                    seller=product.seller,
                    category=product.category,
                ))
            await session.commit()
    except Exception:
        pass

    return product
