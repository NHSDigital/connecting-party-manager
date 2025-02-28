import re
from enum import StrEnum, auto

from domain.core.product_team_key import ProductTeamKey
from domain.core.validation import CpmId


class ProductKeyType(StrEnum):
    GENERAL = auto()

    @property
    def pattern(self) -> re.Pattern:
        return CpmId.General.ID_PATTERN


class ProductKey(ProductTeamKey):
    """A Product Key is a secondary way of indexing / retrieving Products"""

    key_type: ProductKeyType
    key_value: str
