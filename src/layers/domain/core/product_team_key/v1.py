import re
from enum import StrEnum, auto

from domain.core.device_key import DeviceKey
from domain.core.validation import CpmId


class ProductTeamKeyType(StrEnum):
    PRODUCT_TEAM_ID_ALIAS = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case ProductTeamKeyType.PRODUCT_TEAM_ID_ALIAS:
                return CpmId.ProductTeamIdAlias.ID_PATTERN
            case _:
                raise NotImplementedError(f"No ID validation configured for '{self}'")


class ProductTeamKey(DeviceKey):
    """
    A ProductTeam Key is a secondary way of indexing / retrieving Product Teams
    """

    key_type: ProductTeamKeyType
    key_value: str
