from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidShortCodeException, URLNotFoundException
from app.models import URLItem
from app.repositories.url import URLRepository
from app.utils.encoding import decode_base62


class URLService:
    def __init__(self, db: AsyncSession):
        self.repo = URLRepository()
        self.db = db

    async def shorten_url(self, original_url: str) -> URLItem:
        new_url = await self.repo.create(self.db, original_url)
        await self.db.commit()

        await self.db.refresh(new_url)

        return new_url

    async def get_url_details(self, short_code: str) -> str | None:
        try:
            url_id = decode_base62(short_code)
        except ValueError:
            raise InvalidShortCodeException()

        url_obj = await self.repo.get_by_id(self.db, url_id)

        if not url_obj:
            raise URLNotFoundException(payload={"attempted_code": short_code})

        await self.repo.increment_clicks(self.db, url_id)
        await self.db.commit()

        return url_obj

    async def get_url_stats(self, short_code: str) -> URLItem | None:
        """
        Decodes the short_code to ID, then fetches the URL object.
        """
        try:
            url_id = decode_base62(short_code)
        except ValueError:
            raise InvalidShortCodeException(payload={"attempted_code": short_code})

        stats_obj = await self.repo.get_by_id(self.db, url_id)
        if not stats_obj:
            raise URLNotFoundException(payload={"attempted_code": short_code})

        return stats_obj

