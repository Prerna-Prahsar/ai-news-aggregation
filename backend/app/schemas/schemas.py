from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourceTypeEnum(str, Enum):
    rss = "rss"
    api = "api"
    scraper = "scraper"


class PlatformEnum(str, Enum):
    email = "email"
    linkedin = "linkedin"
    whatsapp = "whatsapp"
    blog = "blog"
    newsletter = "newsletter"


class SourceBase(BaseModel):
    name: str
    url: str
    feed_url: Optional[str] = None
    type: SourceTypeEnum = SourceTypeEnum.rss
    active: bool = True


class SourceCreate(SourceBase):
    pass


class SourceOut(SourceBase):
    id: int
    last_fetched: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NewsItemBase(BaseModel):
    title: str
    summary: Optional[str]
    url: str
    author: Optional[str]
    published_at: Optional[datetime]
    tags: List[str] = []
    impact_score: float = 0.5
    image_url: Optional[str] = None


class NewsItemOut(NewsItemBase):
    id: int
    source_id: int
    source: Optional[SourceOut]
    is_duplicate: bool
    is_favorited: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NewsListOut(BaseModel):
    items: List[NewsItemOut]
    total: int
    page: int
    per_page: int


class FavoriteCreate(BaseModel):
    news_item_id: int


class FavoriteOut(BaseModel):
    id: int
    news_item_id: int
    news_item: Optional[NewsItemOut]
    created_at: datetime

    class Config:
        from_attributes = True


class BroadcastRequest(BaseModel):
    favorite_id: int
    platform: PlatformEnum
    recipients: Optional[List[str]] = []
    custom_message: Optional[str] = None


class BroadcastLogOut(BaseModel):
    id: int
    favorite_id: int
    platform: PlatformEnum
    status: str
    message: Optional[str]
    recipients: List[str] = []
    timestamp: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_news: int
    total_sources: int
    total_favorites: int
    total_broadcasts: int
    last_fetched: Optional[datetime]
    top_tags: List[dict]
    sources_breakdown: List[dict]