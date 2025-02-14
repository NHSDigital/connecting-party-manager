from pydantic import BaseModel, Extra, Field


class CreateBookIncomingParams(BaseModel, extra=Extra.forbid):
    title: str = Field(...)
    author: str = Field(...)
    chapters: list[str] = Field(default_factory=list)
