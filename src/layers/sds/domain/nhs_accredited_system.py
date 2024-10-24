from typing import ClassVar, Literal, Optional

from domain.api.sds.query import SearchSDSDeviceQueryParams
from domain.core.questionnaire.v1 import Questionnaire
from domain.repository.questionnaire_repository import QuestionnaireRepository
from domain.repository.questionnaire_repository.v1.questionnaires import (
    QuestionnaireInstance,
)
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
    nhs_mhs_manufacturer_org: Optional[str] = Field(alias="nhsmhsmanufacturerorg")
    nhs_mhs_party_key: str = Field(alias="nhsmhspartykey")
    nhs_product_key: str = Field(alias="nhsproductkey")
    nhs_product_name: Optional[str] = Field(alias="nhsproductname")
    nhs_product_version: Optional[str] = Field(alias="nhsproductversion")
    nhs_as_acf: Optional[set[str]] = Field(alias="nhsasacf")
    nhs_as_client: Optional[set[str]] = Field(alias="nhsasclient")
    nhs_as_svc_ia: set[str] = Field(alias="nhsassvcia")
    nhs_temp_uid: Optional[str] = Field(alias="nhstempuid")
    description: Optional[str] = Field(alias="description")
    nhs_as_category_bag: Optional[set[str]] = Field(alias="nhsascategorybag")

    @classmethod
    def key_fields(cls) -> tuple[str, ...]:
        return ACCREDITED_SYSTEM_KEY_FIELDS

    @classmethod
    def questionnaire(cls) -> Questionnaire:
        repo = QuestionnaireRepository()
        return repo.read(name=QuestionnaireInstance.SPINE_DEVICE)

    @classmethod
    def query_params_model(cls) -> type[SearchSDSDeviceQueryParams]:
        return SearchSDSDeviceQueryParams
