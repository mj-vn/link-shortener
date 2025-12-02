from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from app.api.dependencies import get_url_service
from app.core.decorators import log_analytics
from app.core.logging import logger
from app.schemas import URLResponse, URLCreate
from app.services.url import URLService
from app.utils.encoding import encode_base62

url_manager_router = APIRouter()


@url_manager_router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
)
async def shorten_url(url_obj: URLCreate, url_service: URLService = Depends(get_url_service)):
    """
    Creates a shortened URL.
    """
    result = await url_service.shorten_url(str(url_obj.url))

    logger.info(
        "url_shortened.success",
        original_url=str(url_obj.url),
        short_code=encode_base62(result.short_code),
        db_short_code=result.short_code
    )

    return result


@url_manager_router.get("/{short_code}")
@log_analytics
async def redirect_to_original(
        short_code: str,
        request: Request,
        url_service: URLService = Depends(get_url_service)
):

    original_url = await url_service.get_original_url(short_code)
    if not original_url:
        logger.warning("url_redirect.not_found", code=short_code)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

