from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.api.deps import get_db
from app.core.decorators import log_analytics
from app.schemas.url import URLCreate, URLResponse
from app.services.url import URLService

router = APIRouter()
service = URLService()


@router.post("/shorten", response_model=URLResponse,
             status_code=status.HTTP_201_CREATED)
async def shorten_url(item: URLCreate, db: AsyncSession = Depends(get_db)):
    """
    Creates a shortened URL.
    """
    code = await service.shorten_url(db, str(item.url))

    return {
        "short_code": code,
        "original_url": str(item.url),
        "clicks": 0,
        "created_at": datetime.now()
    }


@router.get("/{short_code}")
@log_analytics
async def redirect_to_original(short_code: str, request: Request,
                               db: AsyncSession = Depends(get_db)):
    original_url = await service.get_original_url(db, short_code)
    if not original_url:
        raise HTTPException(status_code=404, detail="URL not found")

    return RedirectResponse(url=original_url, status_code=307)

