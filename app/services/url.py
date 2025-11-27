from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.url import URLRepository
from app.utils.encoding import encode_base62, decode_base62


class URLService:
    def __init__(self):
        self.repo = URLRepository()

    async def shorten_url(self, db: AsyncSession, original_url: str) -> str:
        # 1. Save to DB -> Get ID (e.g., 3521614606208)
        new_url = await self.repo.create(db, original_url)
        await db.commit()

        # 2. Convert ID to String (e.g., "10000000")
        short_code = encode_base62(new_url.short_code)
        return short_code

    async def get_original_url(self, db: AsyncSession, short_code: str) -> str | None:
        try:
            # 1. Convert String -> ID (e.g., "10000000" -> 3521614606208)
            url_id = decode_base62(short_code)
        except ValueError:
            # If user sends invalid chars like "?", it's not found
            return None

        # 2. Lookup by ID
        url_obj = await self.repo.get_by_id(db, url_id)

        if url_obj:
            # We handle the atomic increment here (or via decorator)
            # Just showing usage of the Repo ID method
            await self.repo.increment_clicks(db, url_id)
            await db.commit()
            return url_obj.original_url

        return None
