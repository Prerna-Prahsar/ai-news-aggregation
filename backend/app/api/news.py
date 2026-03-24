from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.db.database import get_db
from app.models.models import NewsItem, Source, Favorite
from app.schemas.schemas import NewsListOut, NewsItemOut
from app.workers.ingestion_worker import ingest_news

router = APIRouter()


@router.get("/", response_model=NewsListOut)
async def get_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    source: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = Query("date", regex="^(date|impact|source)$"),
    show_duplicates: bool = False,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.is_duplicate == show_duplicates if not show_duplicates else True)
    )
    if search:
        query = query.where(
            or_(NewsItem.title.ilike(f"%{search}%"), NewsItem.summary.ilike(f"%{search}%"))
        )
    if source:
        query = query.join(Source).where(Source.name.ilike(f"%{source}%"))
    if tag:
        query = query.where(NewsItem.tags.contains([tag]))
    if sort == "date":
        query = query.order_by(desc(NewsItem.published_at))
    elif sort == "impact":
        query = query.order_by(desc(NewsItem.impact_score))
    elif sort == "source":
        query = query.join(Source).order_by(Source.name)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()
    query = query.offset((page - 1) * per_page).limit(per_page)
    items = (await db.execute(query)).scalars().all()

    fav_result = await db.execute(select(Favorite.news_item_id).where(Favorite.user_id == 1))
    favorited_ids = set(fav_result.scalars().all())

    out = []
    for item in items:
        d = NewsItemOut.model_validate(item)
        d.is_favorited = item.id in favorited_ids
        out.append(d)

    return NewsListOut(items=out, total=total, page=page, per_page=per_page)


@router.get("/{news_id}", response_model=NewsItemOut)
async def get_news_item(news_id: int, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    result = await db.execute(
        select(NewsItem).options(selectinload(NewsItem.source)).where(NewsItem.id == news_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")
    fav_result = await db.execute(
        select(Favorite).where(Favorite.news_item_id == news_id, Favorite.user_id == 1)
    )
    out = NewsItemOut.model_validate(item)
    out.is_favorited = fav_result.scalars().first() is not None
    return out


@router.post("/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_news)
    return {"message": "News refresh started in background."}


@router.get("/meta/tags")
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsItem.tags).where(NewsItem.is_duplicate == False))
    all_tags = result.scalars().all()
    tag_counter: dict = {}
    for tags in all_tags:
        for tag in (tags or []):
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    sorted_tags = sorted(tag_counter.items(), key=lambda x: -x[1])
    return [{"tag": t, "count": c} for t, c in sorted_tags[:30]]