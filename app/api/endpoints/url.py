from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.deps import get_db, get_url_service
from app.core.decorators import log_analytics
from app.core.logging import logger
from app.schemas import URLResponse, URLCreate
from app.services.url import URLService

url_manager_router = APIRouter()


@url_manager_router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
)
async def shorten_url(url: URLCreate, url_service: URLService = Depends(get_url_service)):
    """
    Creates a shortened URL.
    """
    return await url_service.shorten_url(str(url.url))


@url_manager_router.get("/{short_code}")
@log_analytics
async def redirect_to_original(
        short_code: str,
        request: Request,
        url_service: URLService = Depends(get_url_service)
):

    original_url = await url_service.get_original_url(short_code)
    if not original_url:
        logger.warning("redirect.not_found", code=short_code)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

