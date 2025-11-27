from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.urls import URLItem


class URLRepository:
    async def create(self, db: AsyncSession, original_url: str) -> URLItem:
        db_obj = URLItem(original_url=original_url)
        db.add(db_obj)
        return db_obj

    async def get_by_code(self, db: AsyncSession, short_code: str) -> URLItem | None:
        stmt = select(URLItem).where(URLItem.short_code == short_code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_clicks(self, db: AsyncSession, short_code: str):
        stmt = (
            update(URLItem)
            .where(URLItem.short_code == short_code)
            .values(clicks=URLItem.clicks + 1)
        )
        await db.execute(stmt)

