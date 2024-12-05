from dataclasses import dataclass
from typing import ClassVar, Literal, Optional

from domain.api.sds.query import SearchSDSEndpointQueryParams
from pydantic import Field

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName


@dataclass
class MessageHandlingSystemKey:
    nhs_id_code: str
    nhs_mhs_party_key: str
    nhs_mhs_svc_ia: str


KEY_FIELDS = tuple(MessageHandlingSystemKey.__dataclass_fields__.keys())


class NhsMhs(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName = Field(exclude=True)

    OBJECT_CLASS: ClassVar[Literal["nhsmhs"]] = "nhsmhs"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)

    nhs_approver_urp: str = Field(alias="nhsapproverurp")
    nhs_date_approved: str = Field(alias="nhsdateapproved")
    nhs_date_dns_approved: str = Field(alias="nhsdatednsapproved")
    nhs_date_requested: str = Field(alias="nhsdaterequested")
    nhs_dns_approver: str = Field(alias="nhsdnsapprover")
    nhs_id_code: str = Field(alias="nhsidcode")
    nhs_mhs_cpa_id: Optional[str] = Field(alias="nhsmhscpaid")
    binding: str = Field(alias="binding")
    nhs_mhs_end_point: str = Field(alias="nhsmhsendpoint")
    nhs_mhs_fqdn: str = Field(alias="nhsmhsfqdn")
    nhs_mhs_manufacturer_org: str = Field(alias="nhsmhsmanufacturerorg")
    nhs_mhs_party_key: str = Field(alias="nhsmhspartykey")
    nhs_product_name: Optional[str] = Field(alias="nhsproductname")
    nhs_product_version: Optional[str] = Field(alias="nhsproductversion")
    nhs_requestor_urp: str = Field(alias="nhsrequestorurp")
    nhs_mhs_service_description: Optional[str] = Field(alias="nhsmhsservicedescription")

    nhs_mhs_in: str = Field(alias="nhsmhsin")
    nhs_mhs_sn: str = Field(alias="nhsmhssn")
    nhs_mhs_svc_ia: str = Field(alias="nhsmhssvcia")
    nhs_mhs_retries: Optional[int | Literal[""]] = Field(alias="nhsmhsretries")
    nhs_mhs_retry_interval: Optional[str] = Field(alias="nhsmhsretryinterval")
    nhs_mhs_persist_duration: Optional[str] = Field(alias="nhsmhspersistduration")

    @classmethod
    def query_params_model(cls) -> type[SearchSDSEndpointQueryParams]:
        return SearchSDSEndpointQueryParams
