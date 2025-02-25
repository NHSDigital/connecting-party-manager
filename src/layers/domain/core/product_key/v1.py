import re
from enum import StrEnum, auto

from domain.core.product_team_key import ProductTeamKey
from domain.core.validation import SdsId


class ProductKeyType(StrEnum):
    PARTY_KEY = auto()

    @property
    def pattern(self) -> re.Pattern:
        # To the developer: if adding more patterns then please refer to DeviceKeyType.pattern for guidance
        return SdsId.PartyKey.ID_PATTERN


class ProductKey(ProductTeamKey):
    """A Product Key is a secondary way of indexing / retrieving Products"""

    key_type: ProductKeyType
    key_value: str
