from fastapi import APIRouter, Depends

from app.api.dependencies import get_url_service
from app.core.logging import logger
from app.schemas import URLStatsResponse
from app.services.url import URLService

stats_router = APIRouter()


@stats_router.get("/stats/{short_code}", response_model=URLStatsResponse)
async def get_url_stats(
        short_code: str,
        url_service: URLService = Depends(get_url_service)
):
    url_obj = await url_service.get_url_stats(short_code)

    logger.info("stats.retrieved_success", short_code=short_code)

    return url_obj

