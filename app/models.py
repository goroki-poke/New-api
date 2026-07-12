from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl
from sqlalchemy import String, Float, DateTime, Text, Boolean, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    site: Mapped[str] = mapped_column(String(32), index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    availability: Mapped[str] = mapped_column(String(32), default="in_stock")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[str] = mapped_column(Text, default="[]")
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seller: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Product(BaseModel):
    id: str
    site: str
    url: str
    title: str
    price: float
    currency: str
    availability: str
    description: Optional[str] = None
    images: list[str] = []
    rating: Optional[float] = None
    review_count: Optional[int] = None
    seller: Optional[str] = None
    category: Optional[str] = None
    scraped_at: datetime


class ProductSearchResult(BaseModel):
    query: str
    results: list[Product]
    total: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
