from domain.core.base import BaseModel
from domain.core.device_key.v1 import DeviceKeyType, validate_key
from domain.core.error import InvalidDeviceKeyError
from pydantic import validator


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
        raise InvalidDeviceKeyError(
            f"Key '{key_value}' does not match the expected "
            f"pattern '{key_type.pattern.pattern}' associated with "
            f"key type '{key_type}'"
        )
    return key_value
