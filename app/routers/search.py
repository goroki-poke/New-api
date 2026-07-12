from fastapi import APIRouter, HTTPException, Query

from app.models import Product, ProductSearchResult, ErrorResponse
from app.scrapers import get_scraper

router = APIRouter(prefix="/v1", tags=["search"])


@router.get(
    "/search",
    response_model=ProductSearchResult,
    responses={400: {"model": ErrorResponse}},
    summary="Search products by keyword",
    description="Search an e-commerce site by keyword. Returns a list of matching products with pricing and availability.",
)
async def search_products(
    q: str = Query(..., min_length=1, description="Search keyword (e.g. 'wireless headphones')"),
    site: str = Query("amazon", description="E-commerce site to search"),
    limit: int = Query(10, ge=1, le=50, description="Max results to return"),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    scraper = get_scraper(site)

    try:
        results = await scraper.search(q.strip(), limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search failed: {str(e)}")

    return ProductSearchResult(query=q, results=results, total=len(results))
