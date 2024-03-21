from typing import ClassVar, Literal, Optional

from pydantic import Field
from sds.domain.constants import (
    Authentication,
    InteractionType,
    MhsActor,
    SyncReplyModel,
    YesNoAnswer,
)

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName


class NhsMhs(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName = Field(exclude=True)

    OBJECT_CLASS: ClassVar[Literal["nhsmhs"]] = "nhsmhs"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    nhs_approver_urp: str = Field(alias="nhsapproverurp")
    nhs_contract_property_template_key: str = Field(
        alias="nhscontractpropertytemplatekey"
    )
    nhs_date_approved: str = Field(alias="nhsdateapproved")
    nhs_date_dns_approved: str = Field(alias="nhsdatednsapproved")
    nhs_date_requested: str = Field(alias="nhsdaterequested")
    nhs_dns_approver: str = Field(alias="nhsdnsapprover")
    nhs_ep_interaction_type: InteractionType = Field(alias="nhsepinteractiontype")
    nhs_id_code: str = Field(alias="nhsidcode")
    nhs_mhs_ack_requested: Optional[YesNoAnswer] = Field(alias="nhsmhsackrequested")
    nhs_mhs_cpa_id: str = Field(alias="nhsmhscpaid")
    nhs_mhs_duplicate_elimination: Optional[YesNoAnswer] = Field(
        alias="nhsmhsduplicateelimination"
    )
    nhs_mhs_end_point: str = Field(alias="nhsmhsendpoint")
    nhs_mhs_fqdn: str = Field(alias="nhsmhsfqdn")
    nhs_mhs_in: str = Field(alias="nhsmhsin")
    nhs_mhs_ip_address: Optional[str] = Field(alias="nhsmhsipaddress")
    nhs_mhs_is_authenticated: Authentication = Field(alias="nhsmhsisauthenticated")
    nhs_mhs_manufacturer_org: str = Field(alias="nhsmhsmanufacturerorg")
    nhs_mhs_party_key: str = Field(alias="nhsmhspartykey")
    nhs_mhs_sn: str = Field(alias="nhsmhssn")
    nhs_mhs_svc_ia: str = Field(alias="nhsmhssvcia")
    nhs_mhs_sync_reply_mode: Optional[SyncReplyModel] = Field(
        alias="nhsmhssyncreplymode"
    )
    nhs_product_key: str = Field(alias="nhsproductkey")
    nhs_product_name: Optional[str] = Field(alias="nhsproductname")
    nhs_product_version: Optional[str] = Field(alias="nhsproductversion")
    nhs_requestor_urp: str = Field(alias="nhsrequestorurp")
    nhs_mhs_actor: Optional[MhsActor] = Field(alias="nhsmhsactor")
    nhs_mhs_persist_duration: Optional[str] = Field(alias="nhsmhspersistduration")
    nhs_mhs_retries: Optional[int | Literal[""]] = Field(alias="nhsmhsretries")
    nhs_mhs_retry_interval: Optional[str] = Field(alias="nhsmhsretryinterval")
    nhs_mhs_service_description: Optional[str] = Field(alias="nhsmhsservicedescription")
