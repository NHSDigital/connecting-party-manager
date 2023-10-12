from pydantic import BaseModel, Field

from .constants import VERSION_HEADER_PATTERN


class VersionHeader(BaseModel):
    version: str = Field(pattern=VERSION_HEADER_PATTERN)


class LambdaEventForVersioning(BaseModel):
    headers: VersionHeader
