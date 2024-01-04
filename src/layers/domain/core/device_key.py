import re
from enum import StrEnum, auto

from domain.core.error import InvalidDeviceKeyError
from pydantic import BaseModel, validator

from .validation import ACCREDITED_SYSTEM_ID_REGEX, PRODUCT_ID_REGEX


class DeviceKeyType(StrEnum):
    PRODUCT_ID = auto()
    ACCREDITED_SYSTEM_ID = auto()
    # SERVICE_NOW_ID = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case DeviceKeyType.PRODUCT_ID:
                return PRODUCT_ID_REGEX
            case DeviceKeyType.ACCREDITED_SYSTEM_ID:
                return ACCREDITED_SYSTEM_ID_REGEX
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
