from domain.core.base import BaseModel
from domain.core.device_key.v1 import DeviceKeyType, validate_key
from pydantic import validator


class DeviceKey(BaseModel):
    """
    A Device Key is a secondary way of indexing / retrieving Devices
    """

    key_type: DeviceKeyType
    key_value: str

    @validator("key_value", check_fields=True)
    def validate_key(key_value: str, values: dict):
        key_type: DeviceKeyType = values.get("key_type")
        return validate_key(key=key_value, type=key_type)
