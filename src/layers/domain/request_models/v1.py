from typing import List, Optional

from domain.core.enum import Environment
from domain.core.product_team_key import ProductTeamKey
from pydantic import BaseModel, Extra, Field, root_validator, validator

ALPHANUMERIC_SPACES_AND_UNDERSCORES = r"^[a-zA-Z0-9 _]*$"
ALLOWED_PRODUCT_SEARCH_PARAMS = (
    "product_team_id",
    "organisation_code",
)


class ProductTeamPathParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = Field(...)

    @root_validator(pre=True)
    def ignore_env(cls, values):
        values.pop("environment", None)
        return values


class CreateCpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ensure this value has at least 1 characters")
        return v


class CpmProductReadPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)

    @root_validator(pre=True)
    def ignore_env(cls, values):
        values.pop("environment", None)
        return values


class CpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)

    @root_validator(pre=True)
    def ignore_env(cls, values):
        values.pop("environment", None)
        return values


class SubCpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    environment: Environment


class CreateProductTeamIncomingParams(BaseModel, extra=Extra.forbid):
    ods_code: str = Field(...)
    name: str = Field(...)
    keys: list[ProductTeamKey] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ensure this value has at least 1 characters")
        return v

    @validator("keys")
    def validate_keys(cls, v: List[ProductTeamKey]) -> List[ProductTeamKey]:
        id_count = sum(1 for item in v if item.key_type == "product_team_id")
        if id_count > 1:
            raise ValueError(
                "Ensure that product_team_id only exists once within keys."
            )
        return v


class SearchProductQueryParams(BaseModel, extra=Extra.forbid):
    product_team_id: Optional[str]
    organisation_code: Optional[str]

    @root_validator
    def check_filters(cls, values: dict):
        # Count the number of non-null parameters
        non_empty_params = [
            param for param in values.values() if param is not None and param != 0
        ]

        if len(non_empty_params) != 1:
            raise ValueError(
                f"Please provide exactly one valid query parameter: {ALLOWED_PRODUCT_SEARCH_PARAMS}."
            )

        return values

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
