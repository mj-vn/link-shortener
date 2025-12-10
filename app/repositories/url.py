from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.models import URLAccessLog
from app.models.urls import URLItem


class URLRepository:
    async def create(self, db: AsyncSession, original_url: str, ttl: datetime | None = None) -> URLItem:
        db_obj = URLItem(original_url=original_url, ttl=ttl)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_id(self, db: AsyncSession, url_id: int) -> URLItem | None:
        return await db.get(URLItem, url_id)

    async def increment_clicks(self, db: AsyncSession, url_id: int):
        stmt = update(URLItem).where(URLItem.short_code == url_id).values(clicked_count=URLItem.clicked_count + 1)
        await db.execute(stmt)

    async def log_access(self, db: AsyncSession, url_id: int, ip: str, ua: str):
        log = URLAccessLog(url_id=url_id, ip_address=ip, user_agent=ua)
        db.add(log)
        await db.commit()

