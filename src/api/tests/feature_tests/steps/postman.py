import json
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

POSTMAN_COLLECTION_FILENAME = "postman-collection.json"
BASE_URL = r"{{baseUrl}}/"
OPTIONS = lambda: {"raw": {"language": "json"}}


class HeaderItem(BaseModel):
    key: str
    value: str
    type: Literal["text"] = "text"


class Body(BaseModel):
    raw: str
    mode: Literal["raw"] = "raw"
    options: dict = Field(default_factory=OPTIONS)


class Url(BaseModel):
    raw: str
    host: list[str]
    path: list[str]


class PostmanRequest(BaseModel):
    method: str
    header: list[HeaderItem]
    body: Optional[Body] = None
    url: Url


class PostmanItem(BaseModel):
    name: str
    description: str = Field(default_factory=str)
    request: Optional[PostmanRequest] = None
    item: None | list["PostmanItem"] = Field(default_factory=list)

    def __bool__(self):
        return bool(self.item) or bool(self.request)


class Info(BaseModel):
    name: Literal["Feature Tests"] = "Feature Tests"
    the_schema: Literal[
        "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    ] = Field(
        default="https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        alias="schema",
    )
    description: Literal[
        "The following 'Gherkin' Features demonstrate the behaviour of this API"
    ] = "The following 'Gherkin' Features demonstrate the behaviour of this API"


class PostmanCollection(BaseModel):
    info: Info = Field(default_factory=Info)
    item: list[PostmanItem] = Field(default_factory=list)

    def save(self, path: Path):
        collection = self.dict(exclude_none=True, by_alias=True)
        with open(path / POSTMAN_COLLECTION_FILENAME, "w") as f:
            json.dump(fp=f, obj=collection, indent=4)

    def __bool__(self):
        return bool(self.item)
