from typing import Literal, Optional

from pydantic import BaseModel, Field

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


class StepItem(BaseModel):
    name: str
    request: PostmanRequest = None


class ScenarioItem(BaseModel):
    name: str
    item: list[StepItem] = Field(default_factory=list)


class FeatureItem(BaseModel):
    name: str
    item: list[ScenarioItem] = Field(default_factory=list)


class Info(BaseModel):
    name: Literal["connecting-party-manager"] = "connecting-party-manager"
    the_schema: Literal[
        "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    ] = Field(
        default="https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        alias="schema",
    )


class PostmanCollection(BaseModel):
    info: Info = Field(default_factory=Info)
    item: list[FeatureItem] = Field(default_factory=list)
