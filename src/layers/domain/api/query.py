from typing import Optional

from domain.core.device import DeviceType
from pydantic import BaseModel, Extra, ValidationError, root_validator, validator


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()


class SearchSDSDeviceQueryParams(BaseModel, extra=Extra.forbid):
    nhs_as_client: str
    nhs_as_svc_ia: str
    nhs_mhs_manufacturer_org: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None
    use_mock: Optional[str] = None

    def get_non_null_params(self):
        return self.dict(exclude_none=True)


class SearchSDSEndpointQueryParams(BaseModel, extra=Extra.forbid):
    nhs_id_code: Optional[str] = None
    nhs_mhs_svc_ia: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None
    use_mock: Optional[str] = None

    @root_validator
    def check_filters(cls, values):
        non_empty_count = sum(
            1 for key, value in values if key != "use_mock" and value and value != 0
        )
        if non_empty_count < 2:
            raise ValidationError(
                "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key"
            )

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
