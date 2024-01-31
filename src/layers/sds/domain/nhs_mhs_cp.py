from typing import ClassVar, Literal, Optional

from pydantic import Field
from sds.domain.constants import Authentication, MhsActor, SyncReplyModel, YesNoAnswer

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName


class NhsMhsCp(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName

    OBJECT_CLASS: ClassVar[Literal["nhsmhscp"]] = "nhsmhscp"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    nhs_contract_property_template_key: str = Field(
        alias="nhscontractpropertytemplatekey"
    )
    nhs_mhs_ack_requested: Optional[YesNoAnswer] = Field(alias="nhsmhsackrequested")
    nhs_mhs_action_name: str = Field(alias="nhsmhsactionname")
    nhs_mhs_duplicate_elimination: Optional[YesNoAnswer] = Field(
        alias="nhsmhsduplicateelimination"
    )
    nhs_mhs_is_authenticated: Authentication = Field(alias="nhsmhsisauthenticated")
    nhs_mhs_sync_reply_mode: Optional[SyncReplyModel] = Field(
        alias="nhsmhssyncreplymode"
    )
    nhs_mhs_actor: Optional[MhsActor] = Field(alias="nhsmhsactor")
    nhs_mhs_persist_duration: Optional[str] = Field(alias="nhsmhspersistduration")
    nhs_mhs_retries: Optional[int | Literal[""]] = Field(alias="nhsmhsretries")
    nhs_mhs_retry_interval: Optional[str] = Field(alias="nhsmhsretryinterval")
    nhs_mhs_service_description: Optional[str] = Field(alias="nhsmhsservicedescription")
