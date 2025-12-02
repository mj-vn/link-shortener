import functools
import asyncio
from fastapi import Request
from starlette import status

from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.repositories.url import URLRepository
from app.utils.encoding import decode_base62


def log_analytics(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        short_code = kwargs.get("short_code")
        client_ip = request.client.host if request and request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"

        response = await func(*args, **kwargs)

        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            internal_id = getattr(request.state, "internal_id", None)

            if internal_id is None:
                try:
                    internal_id = decode_base62(short_code)
                except ValueError:
                    return response

            logger.info(
                "url_redirect.success",
                short_code=short_code,
                internal_id=internal_id,
                ip=client_ip
            )

            asyncio.create_task(
                _log_background(internal_id, client_ip, user_agent)
            )

        return response

    return wrapper


async def _log_background(url_id: int, ip: str, ua: str):
    """
    Background task to write logs to DB.
    """
    async with AsyncSessionLocal() as session:
        try:
            repo = URLRepository()
            await repo.log_access(session, url_id, ip, ua)

        except Exception as e:
            logger.error("db_log_write_failed", error=str(e), url_id=url_id)

