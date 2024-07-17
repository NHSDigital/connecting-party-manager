from typing import Optional

from domain.core.device import DeviceType
from pydantic import BaseModel, Extra, validator


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType
    org_code: Optional[str] = None
    interaction_id: Optional[str] = None
    manufacturing_organization: Optional[str] = None
    party_key: Optional[str] = None

    @validator("device_type")
    def validate_device_type(cls, device_type: str):
        return device_type.lower()

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
