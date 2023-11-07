from http import HTTPStatus
from typing import Literal

from pydantic import BaseModel, Field, validator


class ResponseHeaders(BaseModel):
    content_type: Literal["application/json"] = Field(
        default="application/json", alias="Content-Type"
    )
    content_length: int = Field(alias="Content-Length")

    class Config:
        allow_population_by_field_name = True

    def dict(self, *args, by_alias=None, **kwargs):
        return super().dict(*args, by_alias=True, **kwargs)


class Response(BaseModel):
    statusCode: HTTPStatus
    body: str
    headers: ResponseHeaders = None

    @validator("headers", always=True)
    def generate_response_headers(headers, values):
        body: str = values["body"]
        headers = ResponseHeaders(content_length=len(body))
        return headers
