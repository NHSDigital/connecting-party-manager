import re
from enum import StrEnum, auto

from domain.core.error import InvalidDeviceKeyError
from pydantic import validator

from .base import BaseModel
from .validation import CpmId, SdsId


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

    type: DeviceKeyType
    key: str

    @validator("key", check_fields=True)
    def validate_key(key: str, values: dict):
        type: DeviceKeyType = values.get("type")
        return validate_key(key=key, type=type)


def validate_key(key: str, type: DeviceKeyType):
    if type and type.pattern.match(key) is None:
        raise InvalidDeviceKeyError(
            f"Key '{key}' does not match the expected "
            f"pattern '{type.pattern.pattern}' associated with "
            f"key type '{type}'"
        )
    return key
