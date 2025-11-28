from datetime import datetime

from app.schemas.base_schema import CamelBaseModel, ShortCodeField


class URLStatsResponse(CamelBaseModel):
    short_code: ShortCodeField

    original_url: str
    clicked_count: int
    created_at: datetime

