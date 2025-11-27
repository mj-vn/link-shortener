import functools
from fastapi import Request
from app.db.session import AsyncSessionLocal
from app.repositories.url import URLRepository
from app.utils.encoding import decode_base62

repo = URLRepository()


def log_analytics(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)

        short_code = kwargs.get('short_code')
        request: Request = kwargs.get('request')

        if response.status_code == 307 and short_code and request:
            try:
                url_id = decode_base62(short_code)
                ip = request.client.host
                ua = request.headers.get("user-agent")

                import asyncio
                asyncio.create_task(_log_background(url_id, ip, ua))
            except ValueError:
                pass  # Invalid code, don't log

        return response

    return wrapper


async def _log_background(url_id: int, ip: str, ua: str):
    async with AsyncSessionLocal() as session:
        await repo.log_access(session, url_id, ip, ua)

