from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables
from app.routers import products, search, health
from app.middleware.rapidapi import RapidAPIMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_tables()
    except Exception:
        pass
    yield


app = FastAPI(
    title="E-Commerce Product Data API",
    description="Scrape product details, prices, and availability from major e-commerce sites. "
                "Returns clean structured JSON. Ideal for price comparison, shopping apps, and inventory tracking.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RapidAPIMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(search.router)
