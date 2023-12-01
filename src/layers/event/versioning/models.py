from pydantic import BaseModel


class VersionHeader(BaseModel):
    version: int


class LambdaEventForVersioning(BaseModel):
    headers: VersionHeader
