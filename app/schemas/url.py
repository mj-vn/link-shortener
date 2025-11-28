from pydantic import BaseModel, HttpUrl
from datetime import datetime

from app.schemas.base_schema import ShortCodeField, CamelBaseModel


class URLCreate(CamelBaseModel):
    url: HttpUrl


class URLResponse(CamelBaseModel):

    short_code: ShortCodeField
    original_url: str
    created_at: datetime
    clicked_count: int

