from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLCreate(BaseModel):
    url: HttpUrl


class URLResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    clicks: int

    class Config:
        from_attributes = True

