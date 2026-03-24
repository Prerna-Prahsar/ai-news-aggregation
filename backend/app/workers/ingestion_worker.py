import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.models import Source, NewsItem
from app.services.fetcher import fetch_all_sources, AI_SOURCES
from app.services.deduplicator import deduplicate
from app.core.config import settings

logger = logging.getLogger(__name__)


async def seed_sources(db: AsyncSession):
    result = await db.execute(select(Source))
    existing = result.scalars().all()
    if existing:
        return
    for s in AI_SOURCES:
        source = Source(
            name=s["name"],
            url=s["url"],
            feed_url=s.get("feed_url", s["url"]),
            type=s.get("type", "rss"),
            active=True,
        )
        db.add(source)
    await db.commit()
    logger.info(f"Seeded {len(AI_SOURCES)} sources.")


async def ingest_news():
    async with AsyncSessionLocal() as db:
        await seed_sources(db)

        result = await db.execute(select(Source).where(Source.active == True))
        sources_list = result.scalars().all()
        source_map = {s.name: s.id for s in sources_list}

        raw_items = await fetch_all_sources()
        processed, dup_count = deduplicate(raw_items)
        logger.info(f"After dedup: {len(processed)} items ({dup_count} duplicates)")

        added = 0
        for item in processed:
            exists = await db.execute(
                select(NewsItem).where(NewsItem.url == item["url"])
            )
            if exists.scalars().first():
                continue
            source_id = source_map.get(item.get("source_name", ""), None)
            if not source_id and sources_list:
                source_id = sources_list[0].id
            news = NewsItem(
                source_id=source_id,
                title=item["title"],
                summary=item.get("summary"),
                url=item["url"],
                author=item.get("author"),
                published_at=item.get("published_at"),
                tags=item.get("tags", []),
                is_duplicate=item.get("is_duplicate", False),
                impact_score=item.get("impact_score", 0.5),
            )
            db.add(news)
            added += 1

        await db.commit()

        for source in sources_list:
            source.last_fetched = datetime.now(tz=timezone.utc)
        await db.commit()

    return added


async def run_worker():
    interval = settings.FETCH_INTERVAL_MINUTES * 60
    logger.info(f"Worker started. Interval: {settings.FETCH_INTERVAL_MINUTES} minutes")
    while True:
        try:
            added = await ingest_news()
            logger.info(f"Ingestion done. Added {added} items.")
        except Exception as e:
            logger.error(f"Ingestion error: {e}", exc_info=True)
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(run_worker())