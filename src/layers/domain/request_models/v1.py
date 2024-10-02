from domain.core.product_team_key import ProductTeamKey
from pydantic import BaseModel, Extra, Field


class ProductTeamPathParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = Field(...)


class CreateCpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    product_name: str = Field(...)


class CpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)


class CreateProductTeamIncomingParams(BaseModel, extra=Extra.forbid):
    ods_code: str = Field(...)
    name: str = Field(...)
    keys: list[ProductTeamKey] = Field(default_factory=list)
