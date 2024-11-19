import re
from enum import StrEnum, auto

from domain.core.base import BaseModel
from domain.core.error import InvalidKeyPattern
from domain.core.validation import CpmId, SdsId
from pydantic import validator


class DeviceKeyType(StrEnum):
    PRODUCT_ID = auto()
    ACCREDITED_SYSTEM_ID = auto()
    MESSAGE_HANDLING_SYSTEM_ID = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case DeviceKeyType.PRODUCT_ID:
                return CpmId.Product.ID_PATTERN
            case DeviceKeyType.ACCREDITED_SYSTEM_ID:
                return SdsId.AccreditedSystem.ID_PATTERN
            case DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID:
                return SdsId.MessageHandlingSystem.ID_PATTERN
            case _:
                raise NotImplementedError(f"No ID validation configured for '{self}'")


class DeviceKey(BaseModel):
    """
    A Device Key is a secondary way of indexing / retrieving Devices
    """

    key_type: DeviceKeyType
    key_value: str

    @validator("key_value", check_fields=True)
    def validate_key(cls, key_value: str, values: dict):
        key_type: DeviceKeyType = values.get("key_type")
        return validate_key(key_value=key_value, key_type=key_type)

    @property
    def parts(self):
        return (self.key_type, self.key_value)

    def __hash__(self):
        return hash(self.parts)


def validate_key(key_value: str, key_type: DeviceKeyType):
    if key_type and key_type.pattern.match(key_value) is None:
        raise InvalidKeyPattern(
            f"Key '{key_value}' does not match the expected "
            f"pattern '{key_type.pattern.pattern}' associated with "
            f"key type '{key_type}'"
        )
    return key_value
