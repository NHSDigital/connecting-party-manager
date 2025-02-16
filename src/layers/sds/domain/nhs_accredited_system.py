from typing import ClassVar, Literal, Optional

from domain.api.sds.query import SearchSDSDeviceQueryParams
from pydantic import Field

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName

ACCREDITED_SYSTEM_KEY_FIELDS = ("nhs_as_client",)


class NhsAccreditedSystem(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName = Field(exclude=True)

    OBJECT_CLASS: ClassVar[Literal["nhsas"]] = "nhsas"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    nhs_approver_urp: str = Field(alias="nhsapproverurp")
    nhs_date_approved: str = Field(alias="nhsdateapproved")
    nhs_requestor_urp: str = Field(alias="nhsrequestorurp")
    nhs_date_requested: str = Field(alias="nhsdaterequested")
    nhs_id_code: str = Field(alias="nhsidcode")
    nhs_mhs_manufacturer_org: str = Field(alias="nhsmhsmanufacturerorg")
    nhs_mhs_party_key: str = Field(alias="nhsmhspartykey")
    nhs_product_key: str = Field(alias="nhsproductkey")
    nhs_product_name: str = Field(alias="nhsproductname", default=None)
    nhs_product_version: str = Field(alias="nhsproductversion", default=None)
    nhs_as_acf: Optional[set[str]] = Field(alias="nhsasacf")
    nhs_as_client: set[str] = Field(alias="nhsasclient", default_factory=set)
    nhs_as_svc_ia: set[str] = Field(alias="nhsassvcia")
    nhs_temp_uid: str = Field(alias="nhstempuid", default=None)
    description: Optional[str] = Field(alias="description")
    nhs_as_category_bag: Optional[set[str]] = Field(alias="nhsascategorybag")

    @classmethod
    def query_params_model(cls) -> type[SearchSDSDeviceQueryParams]:
        return SearchSDSDeviceQueryParams
