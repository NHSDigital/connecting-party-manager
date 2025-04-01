from http import HTTPStatus
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class AwsLambdaResponseHeaders(BaseModel):
    content_type: Literal["application/json"] = Field(
        default="application/json", alias="Content-Type"
    )
    content_length: str = Field(alias="Content-Length", regex=r"^[0-9][0-9]*$")
    version: str = Field(alias="Version", regex=r"^(null)|([1-9][0-9]*)$")
    host: str = Field(default=None, alias="Host")

    class Config:
        allow_population_by_field_name = True

    def dict(self, *args, by_alias=None, **kwargs):
        return super().dict(*args, by_alias=True, **kwargs)


class AwsLambdaResponse(BaseModel):
    statusCode: HTTPStatus
    body: str = Field(min_length=0, default="")
    version: None | str = Field(exclude=True)
    headers: Optional[AwsLambdaResponseHeaders]

    @validator("headers", always=True)
    def generate_response_headers(cls, headers, values):
        if headers is not None:
            return headers
        body: str = values["body"]
        version: None | str = values["version"]
        headers = AwsLambdaResponseHeaders(
            content_length=len(body),
            version="null" if version is None else version,
            host="foo.co.uk",
        )
        return headers

    def dict(self):
        """Convert statusCode to native python integer"""
        data = super().dict()
        data["statusCode"] = data["statusCode"].value
        return data
