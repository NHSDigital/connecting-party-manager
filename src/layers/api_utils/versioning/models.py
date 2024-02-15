from pydantic import BaseModel


class VersionHeader(BaseModel):
    version: int


class Event(BaseModel):
    headers: VersionHeader
