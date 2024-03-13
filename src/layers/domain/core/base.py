from types import FunctionType

import orjson
from pydantic import BaseModel as _BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(_BaseModel):
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            set: list,
            FunctionType: lambda fn: fn.__name__,
            type: lambda _type: _type.__name__,
        }
        json_dumps = orjson_dumps
