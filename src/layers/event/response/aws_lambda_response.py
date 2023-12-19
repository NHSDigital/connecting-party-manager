from http import HTTPStatus
from typing import Literal

from pydantic import BaseModel, Field, validator


class AwsLambdaResponseHeaders(BaseModel):
    content_type: Literal["application/json"] = Field(
        default="application/json", alias="Content-Type"
    )
    content_length: str = Field(alias="Content-Length", regex=r"^[1-9][0-9]*$")

    class Config:
        allow_population_by_field_name = True

    def dict(self, *args, by_alias=None, **kwargs):
        return super().dict(*args, by_alias=True, **kwargs)


class AwsLambdaResponse(BaseModel):
    statusCode: HTTPStatus
    body: str = Field(min_length=1)
    headers: AwsLambdaResponseHeaders = None

    @validator("headers", always=True)
    def generate_response_headers(headers, values):
        body: str = values["body"]
        headers = AwsLambdaResponseHeaders(content_length=len(body))
        return headers

    def dict(self):
        """Convert statusCode to native python integer"""
        data = super().dict()
        data["statusCode"] = data["statusCode"].value
        return data
