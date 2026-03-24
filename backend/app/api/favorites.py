from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.models import Favorite, NewsItem, User
from app.schemas.schemas import FavoriteOut, FavoriteCreate, NewsItemOut

router = APIRouter()


async def get_or_create_user(db: AsyncSession) -> int:
    result = await db.execute(select(User).where(User.id == 1))
    user = result.scalars().first()
    if not user:
        user = User(id=1, name="Admin", email="admin@example.com", role="admin")
        db.add(user)
        await db.commit()
    return 1


@router.get("/", response_model=list[FavoriteOut])
async def get_favorites(db: AsyncSession = Depends(get_db)):
    await get_or_create_user(db)
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.news_item).selectinload(NewsItem.source))
        .where(Favorite.user_id == 1)
        .order_by(Favorite.created_at.desc())
    )
    favs = result.scalars().all()
    out = []
    for f in favs:
        d = FavoriteOut.model_validate(f)
        if f.news_item:
            ni_out = NewsItemOut.model_validate(f.news_item)
            ni_out.is_favorited = True
            d.news_item = ni_out
        out.append(d)
    return out


@router.post("/", response_model=FavoriteOut)
async def add_favorite(body: FavoriteCreate, db: AsyncSession = Depends(get_db)):
    await get_or_create_user(db)
    ni_result = await db.execute(select(NewsItem).where(NewsItem.id == body.news_item_id))
    if not ni_result.scalars().first():
        raise HTTPException(status_code=404, detail="News item not found")
    existing = await db.execute(
        select(Favorite).where(Favorite.news_item_id == body.news_item_id, Favorite.user_id == 1)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Already in favorites")
    fav = Favorite(user_id=1, news_item_id=body.news_item_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.news_item).selectinload(NewsItem.source))
        .where(Favorite.id == fav.id)
    )
    return FavoriteOut.model_validate(result.scalars().first())


@router.delete("/{favorite_id}")
async def remove_favorite(favorite_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == 1)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()
    return {"message": "Removed from favorites"}


@router.delete("/by-news/{news_item_id}")
async def remove_favorite_by_news(news_item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite).where(Favorite.news_item_id == news_item_id, Favorite.user_id == 1)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()
    return {"message": "Removed from favorites"}