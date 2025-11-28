from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime

from app.utils.encoding import encode_base62


class URLCreate(BaseModel):
    url: HttpUrl


class URLResponse(BaseModel):

    short_code: str
    original_url: str
    created_at: datetime
    clicks: int


    @field_validator('short_code', mode='before')
    @classmethod
    def transform_id_to_code(cls, v):
        if isinstance(v, int):
            return encode_base62(v)
        return v

    class Config:
        from_attributes = True
