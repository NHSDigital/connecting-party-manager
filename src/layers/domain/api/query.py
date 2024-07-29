from typing import Optional

from domain.core.device import DeviceType
from pydantic import BaseModel, Extra, ValidationError, root_validator, validator


class SearchQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()


class SearchSDSDeviceQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType
    nhs_as_client: Optional[str] = None
    nhs_as_svc_ia: Optional[str] = None
    nhs_id_code: Optional[str] = None
    nhs_mhs_svc_ia: Optional[str] = None
    nhs_mhs_manufacturer_org: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None
    use_mock: Optional[str] = None

    @root_validator
    def check_filters(cls, values):
        device_type = values.get("device_type")
        nhs_as_client = values.get("nhs_as_client")
        nhs_as_svc_ia = values.get("nhs_as_svc_ia")
        nhs_id_code = values.get("nhs_id_code")
        nhs_mhs_svc_ia = values.get("nhs_mhs_svc_ia")
        nhs_mhs_manufacturer_org = values.get("nhs_mhs_manufacturer_org")

        if device_type.lower() == "product":
            if nhs_id_code or nhs_mhs_svc_ia:
                raise ValidationError(
                    "nhs_id_code and nhs_mhs_svc_ia filters are not allowed when device type is product."
                )
        else:
            if nhs_as_client or nhs_as_svc_ia or nhs_mhs_manufacturer_org:
                raise ValidationError(
                    "nhs_as_client, nhs_mhs_manufacturer_org and nhs_as_svc_ia filters are not allowed when device type is endpoint."
                )

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()

    def get_non_null_params(self):
        return self.dict(exclude_none=True)


class SearchSDSEndpointQueryParams(BaseModel, extra=Extra.forbid):
    device_type: DeviceType
    nhs_as_client: Optional[str] = None
    nhs_as_svc_ia: Optional[str] = None
    nhs_id_code: Optional[str] = None
    nhs_mhs_svc_ia: Optional[str] = None
    nhs_mhs_manufacturer_org: Optional[str] = None
    nhs_mhs_party_key: Optional[str] = None
    use_mock: Optional[str] = None

    @root_validator
    def check_filters(cls, values):
        device_type = values.get("device_type")
        nhs_as_client = values.get("nhs_as_client")
        nhs_as_svc_ia = values.get("nhs_as_svc_ia")
        nhs_id_code = values.get("nhs_id_code")
        nhs_mhs_svc_ia = values.get("nhs_mhs_svc_ia")
        nhs_mhs_manufacturer_org = values.get("nhs_mhs_manufacturer_org")

        if device_type.lower() == "product":
            if nhs_id_code or nhs_mhs_svc_ia:
                raise ValidationError(
                    "nhs_id_code and nhs_mhs_svc_ia filters are not allowed when device type is product."
                )
        else:
            if nhs_as_client or nhs_as_svc_ia or nhs_mhs_manufacturer_org:
                raise ValidationError(
                    "nhs_as_client, nhs_mhs_manufacturer_org and nhs_as_svc_ia filters are not allowed when device type is endpoint."
                )

    @validator("device_type")
    def validate_device_type(device_type: str):
        return device_type.lower()

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
