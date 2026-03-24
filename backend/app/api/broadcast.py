from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.models import Favorite, BroadcastLog, NewsItem, BroadcastStatus
from app.schemas.schemas import BroadcastRequest, BroadcastLogOut
from app.services.broadcaster import broadcast

router = APIRouter()


@router.post("/", response_model=BroadcastLogOut)
async def send_broadcast(body: BroadcastRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.news_item).selectinload(NewsItem.source))
        .where(Favorite.id == body.favorite_id)
    )
    fav = result.scalars().first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    ni = fav.news_item
    source_name = ni.source.name if ni.source else "Unknown"

    result_data = broadcast(
        platform=body.platform.value,
        title=ni.title,
        summary=ni.summary or "",
        url=ni.url,
        source=source_name,
        author=ni.author or "",
        recipients=body.recipients or [],
    )

    status_val = result_data.get("status", "failed")
    if status_val == "sent":
        db_status = BroadcastStatus.SENT
    elif status_val == "simulated":
        db_status = BroadcastStatus.SIMULATED
    else:
        db_status = BroadcastStatus.FAILED

    log = BroadcastLog(
        favorite_id=body.favorite_id,
        platform=body.platform.value,
        status=db_status,
        message=result_data.get("message") or result_data.get("caption"),
        recipients=body.recipients or [],
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return BroadcastLogOut.model_validate(log)


@router.get("/logs", response_model=list[BroadcastLogOut])
async def get_broadcast_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BroadcastLog).order_by(BroadcastLog.timestamp.desc()).limit(100)
    )
    return [BroadcastLogOut.model_validate(l) for l in result.scalars().all()]