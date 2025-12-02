from typing import Any, Annotated

from pydantic import BaseModel, ConfigDict, BeforeValidator
from pydantic.alias_generators import to_camel

from app.utils.encoding import encode_base62


class CamelBaseModel(BaseModel):
    """
    A base model that automatically converts snake_case fields to camelCase for JSON output.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


def convert_int_id_to_str_code(v: Any) -> str:
    if isinstance(v, int):
        return encode_base62(v)
    return str(v)


ShortCodeField = Annotated[str, BeforeValidator(convert_int_id_to_str_code)]

