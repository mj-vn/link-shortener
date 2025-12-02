from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.api.dependencies import get_url_service
from app.schemas import URLStatsResponse
from app.services.url import URLService

stats_router = APIRouter()


@stats_router.get("/stats/{short_code}", response_model=URLStatsResponse)
async def get_url_stats(
        short_code: str,
        url_service: URLService = Depends(get_url_service)
):
    url_obj = await url_service.get_url_stats(short_code)

    if not url_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    return url_obj

