from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class SourceType(str, enum.Enum):
    RSS = "rss"
    API = "api"
    SCRAPER = "scraper"


class BroadcastPlatform(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    WHATSAPP = "whatsapp"
    BLOG = "blog"
    NEWSLETTER = "newsletter"


class BroadcastStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SIMULATED = "simulated"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    feed_url = Column(String(500))
    type = Column(SAEnum(SourceType), default=SourceType.RSS)
    active = Column(Boolean, default=True)
    last_fetched = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news_items = relationship("NewsItem", back_populates="source")


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    url = Column(String(1000), nullable=False, unique=True)
    author = Column(String(200))
    published_at = Column(DateTime(timezone=True))
    tags = Column(JSON, default=list)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, ForeignKey("news_items.id"), nullable=True)
    impact_score = Column(Float, default=0.5)
    image_url = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("Source", back_populates="news_items")
    favorites = relationship("Favorite", back_populates="news_item")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=1)
    news_item_id = Column(Integer, ForeignKey("news_items.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news_item = relationship("NewsItem", back_populates="favorites")
    user = relationship("User", back_populates="favorites")
    broadcast_logs = relationship("BroadcastLog", back_populates="favorite")


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id = Column(Integer, primary_key=True, index=True)
    favorite_id = Column(Integer, ForeignKey("favorites.id"), nullable=False)
    platform = Column(SAEnum(BroadcastPlatform), nullable=False)
    status = Column(SAEnum(BroadcastStatus), default=BroadcastStatus.PENDING)
    message = Column(Text)
    recipients = Column(JSON, default=list)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    favorite = relationship("Favorite", back_populates="broadcast_logs")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, default="Admin")
    email = Column(String(300), unique=True, nullable=False, default="admin@example.com")
    role = Column(String(50), default="admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    favorites = relationship("Favorite", back_populates="user")