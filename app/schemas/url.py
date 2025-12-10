from typing import Optional

from pydantic import HttpUrl, field_validator
from datetime import datetime

from app.schemas.base_schema import ShortCodeField, CamelBaseModel


class URLCreate(CamelBaseModel):
    url: HttpUrl
    ttl: Optional[datetime]

    @field_validator('ttl')
    def check_ttl_is_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v

        current_time = datetime.utcnow()
        if v <= current_time:
            raise ValueError('TTL must be in the future')

        return v


class URLResponse(CamelBaseModel):

    short_code: ShortCodeField
    original_url: str
    created_at: datetime
    clicked_count: int
    ttl: Optional[datetime]

