from typing import ClassVar, Literal, Optional

from pydantic import Field

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName


class NhsMhsService(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName

    OBJECT_CLASS: ClassVar[Literal["nhsmhsservice"]] = "nhsmhsservice"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    nhs_approver_urp: str = Field(alias="nhsapproverurp")
    nhs_date_approved: str = Field(alias="nhsdateapproved")
    nhs_requestor_urp: Optional[str] = Field(alias="nhsrequestorurp")
    nhs_date_requested: str = Field(alias="nhsdaterequested")
    nhs_dns_approver: str = Field(alias="nhsdnsapprover")
    nhs_date_dns_approved: str = Field(alias="nhsdatednsapproved")
    nhs_id_code: str = Field(alias="nhsidcode")
    nhs_mhs_manufacturer_org: str = Field(alias="nhsmhsmanufacturerorg")
    nhs_mhs_party_key: str = Field(alias="nhsmhspartykey")
    nhs_mhs_service_name: str = Field(alias="nhsmhsservicename")
    nhs_product_key: str = Field(alias="nhsproductkey")
    nhs_mhs_service_description: Optional[str] = Field(alias="nhsmhsservicedescription")
