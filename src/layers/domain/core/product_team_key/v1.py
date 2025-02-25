import re
from enum import StrEnum, auto

from domain.core.base import BaseModel
from domain.core.error import InvalidKeyPattern
from domain.core.validation import CpmId
from pydantic import validator


class ProductTeamKeyType(StrEnum):
    PRODUCT_TEAM_ID_ALIAS = auto()
    EPR_ID = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case ProductTeamKeyType.PRODUCT_TEAM_ID_ALIAS:
                return CpmId.ProductTeamIdAlias.ID_PATTERN
            case ProductTeamKeyType.EPR_ID:
                return CpmId.EprId.ID_PATTERN
            case _:
                raise NotImplementedError(f"No ID validation configured for '{self}'")


class ProductTeamKey(BaseModel):
    """
    A ProductTeam Key is a secondary way of indexing / retrieving Product Teams
    """

    key_type: ProductTeamKeyType
    key_value: str

    @validator("key_value", check_fields=True)
    def validate_key(cls, key_value: str, values: dict):
        key_type: ProductTeamKeyType = values.get("key_type")
        return validate_key(key_value=key_value, key_type=key_type)

    @property
    def parts(self):
        return (self.key_type, self.key_value)

    def __hash__(self):
        return hash(self.parts)


def validate_key(key_value: str, key_type: ProductTeamKeyType):
    if key_type and key_type.pattern.match(key_value) is None:
        raise InvalidKeyPattern(
            f"Key '{key_value}' does not match the expected "
            f"pattern '{key_type.pattern.pattern}' associated with "
            f"key type '{key_type}'"
        )
    return key_value
