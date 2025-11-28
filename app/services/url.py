from sqlalchemy.ext.asyncio import AsyncSession

from app.models import URLItem
from app.repositories.url import URLRepository
from app.utils.encoding import encode_base62, decode_base62


class URLService:
    def __init__(self):
        self.repo = URLRepository()

    async def shorten_url(self, db: AsyncSession, original_url: str) -> URLItem:
        new_url = await self.repo.create(db, original_url)
        await db.commit()

        await db.refresh(new_url)

        return new_url

    async def get_original_url(self, db: AsyncSession, short_code: str) -> str | None:
        try:
            url_id = decode_base62(short_code)
        except ValueError:
            return None

        url_obj = await self.repo.get_by_id(db, url_id)

        if url_obj:
            # Handle the atomic increment here (or via decorator)
            await self.repo.increment_clicks(db, url_id)
            await db.commit()
            return url_obj.original_url

        return None

    async def get_url_stats(self, db: AsyncSession, short_code: str) -> URLItem | None:
        """
        Decodes the short_code to ID, then fetches the URL object.
        """
        try:
            url_id = decode_base62(short_code)
        except ValueError:
            # Short code contains invalid characters
            return None

        return await self.repo.get_by_id(db, url_id)

