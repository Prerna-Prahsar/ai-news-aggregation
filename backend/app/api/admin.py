from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.db.database import get_db
from app.models.models import NewsItem, Source, Favorite, BroadcastLog
from app.schemas.schemas import DashboardStats
from app.workers.ingestion_worker import ingest_news

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_news = (await db.execute(
        select(func.count(NewsItem.id)).where(NewsItem.is_duplicate == False)
    )).scalar_one()
    total_sources = (await db.execute(
        select(func.count(Source.id)).where(Source.active == True)
    )).scalar_one()
    total_favorites = (await db.execute(select(func.count(Favorite.id)))).scalar_one()
    total_broadcasts = (await db.execute(select(func.count(BroadcastLog.id)))).scalar_one()

    last_fetched = (await db.execute(
        select(Source.last_fetched)
        .where(Source.last_fetched != None)
        .order_by(desc(Source.last_fetched)).limit(1)
    )).scalar_one_or_none()

    tags_r = await db.execute(
        select(NewsItem.tags).where(NewsItem.is_duplicate == False).limit(200)
    )
    tag_counter: dict = {}
    for tags in tags_r.scalars().all():
        for t in (tags or []):
            tag_counter[t] = tag_counter.get(t, 0) + 1
    top_tags = sorted(tag_counter.items(), key=lambda x: -x[1])[:10]

    src_r = await db.execute(
        select(Source.name, func.count(NewsItem.id).label("count"))
        .join(NewsItem, NewsItem.source_id == Source.id)
        .where(NewsItem.is_duplicate == False)
        .group_by(Source.name)
        .order_by(desc("count"))
        .limit(10)
    )
    sources_breakdown = [{"source": r[0], "count": r[1]} for r in src_r.all()]

    return DashboardStats(
        total_news=total_news,
        total_sources=total_sources,
        total_favorites=total_favorites,
        total_broadcasts=total_broadcasts,
        last_fetched=last_fetched,
        top_tags=[{"tag": t, "count": c} for t, c in top_tags],
        sources_breakdown=sources_breakdown,
    )


@router.post("/seed")
async def seed_and_fetch(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_news)
    return {"message": "Seeding and fetching started in background."}