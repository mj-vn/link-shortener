from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas import URLStatsResponse
from app.services.url import URLService

stats_router = APIRouter()
service = URLService()


@stats_router.get("/stats/{short_code}", response_model=URLStatsResponse)
async def get_url_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    url_obj = await service.get_url_stats(db, short_code)

    if not url_obj:
        raise HTTPException(status_code=404, detail="URL not found")

    return url_obj

