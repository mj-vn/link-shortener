from datetime import datetime
from typing import Any, Annotated

from pydantic import BaseModel, BeforeValidator

from app.utils.encoding import encode_base62


# Helper function to transform data
def convert_int_id_to_str_code(v: Any) -> str:
    if isinstance(v, int):
        return encode_base62(v)
    return str(v)


class URLStatsResponse(BaseModel):
    short_code: Annotated[str, BeforeValidator(convert_int_id_to_str_code)]

    original_url: str
    clicked_count: int
    created_at: datetime

    class Config:
        from_attributes = True

