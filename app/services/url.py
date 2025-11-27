from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url import URLRepository
from app.utils.encoding import encode_base62
from app.models.urls import URLItem


class URLService:
    def __init__(self):
        self.repo = URLRepository()

    async def shorten_url(self, db: AsyncSession, original_url: str) -> URLItem:
        new_url = await self.repo.create(db, original_url)
        await db.flush()

        code = encode_base62(new_url.id)
        new_url.short_code = code

        await db.commit()
        await db.refresh(new_url)
        return new_url

    async def get_original_url(self, db: AsyncSession, short_code: str) -> str | None:
        url_obj = await self.repo.get_by_code(db, short_code)
        if url_obj:
            # Atomic Increment
            await self.repo.increment_clicks(db, short_code)
            await db.commit()
            return url_obj.original_url
        return None

