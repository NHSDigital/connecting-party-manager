from domain.core.device import DeviceType
from pydantic import BaseModel, Extra, validator


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType
    org_code: str
    interaction_id: str
    manufacturing_organization: str
    party_key: str

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()
