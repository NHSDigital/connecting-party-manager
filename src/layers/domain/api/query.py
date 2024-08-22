from domain.core.device import DeviceType
from pydantic import BaseModel, Extra, validator


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()
