import re
from enum import StrEnum, auto

from domain.core.base import BaseModel
from domain.core.error import InvalidDeviceKeyError
from domain.core.validation import SdsId
from pydantic import validator


class DeviceKeyType(StrEnum):
    ACCREDITED_SYSTEM_ID = auto()
    MESSAGE_HANDLING_SYSTEM_ID = auto()

    @property
    def pattern(self) -> re.Pattern:
        match self:
            case DeviceKeyType.ACCREDITED_SYSTEM_ID:
                return SdsId.AccreditedSystem.ID_PATTERN
            case DeviceKeyType.MESSAGE_HANDLING_SYSTEM_ID:
                return SdsId.MessageHandlingSystem.ID_PATTERN


class DeviceKey(BaseModel):
    """
    A Device Key is a secondary way of indexing / retrieving Devices
    """

    type: DeviceKeyType
    key: str

    @validator("key", check_fields=True)
    def validate_key(cls, key: str, values: dict):
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
