from typing import ClassVar, Literal, Optional

from pydantic import Field
from sds.domain.constants import InteractionType

from .base import OBJECT_CLASS_FIELD_NAME, SdsBaseModel
from .organizational_unit import OrganizationalUnitDistinguishedName


class NhsMhsAction(SdsBaseModel):
    distinguished_name: OrganizationalUnitDistinguishedName

    OBJECT_CLASS: ClassVar[Literal["nhsmhsaction"]] = "nhsmhsaction"
    object_class: str = Field(alias=OBJECT_CLASS_FIELD_NAME)
    unique_identifier: str = Field(alias="uniqueidentifier")

    nhs_approver_urp: str = Field(alias="nhsapproverurp")
    nhs_date_approved: str = Field(alias="nhsdateapproved")
    nhs_requestor_urp: Optional[str] = Field(alias="nhsrequestorurp")
    nhs_date_requested: str = Field(alias="nhsdaterequested")
    nhs_dns_approver: str = Field(alias="nhsdnsapprover")
    nhs_date_dns_approved: str = Field(alias="nhsdatednsapproved")
    nhs_ep_interaction_type: InteractionType = Field(
        alias="nhsepinteractiontype",
    )
    nhs_mhs_action_name: str = Field(alias="nhsmhsactionname")
    nhs_mhs_end_point: str = Field(alias="nhsmhsendpoint")
