import functools
import asyncio
from fastapi import Request
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

        log = logger.bind(
            short_code=short_code,
            ip=request.client.host if request else "unknown",
            user_agent=request.headers.get(
                "user-agent",
                "unknown"
            ) if request else "unknown"
        )

        try:
            response = await func(*args, **kwargs)

            if response.status_code == 307:
                log.info("url_redirect_success")

                try:
                    url_id = decode_base62(short_code)

                    asyncio.create_task(
                        _log_background(
                            url_id,
                            request.client.host if request else "unknown",
                            request.headers.get("user-agent",
                                                "unknown") if request else "unknown"
                        )
                    )
                except ValueError:
                    log.warning("invalid_short_code_format")

            return response

        except Exception as e:
            log.error("url_redirect_failed", error=str(e))
            raise e

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

