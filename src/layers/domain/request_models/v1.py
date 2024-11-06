from collections import defaultdict
from typing import Literal

from domain.core.device import AS_DEVICE_NAME, MHS_DEVICE_NAME
from domain.core.product_team_key import ProductTeamKey
from domain.repository.questionnaire_repository import QuestionnaireInstance
from pydantic import BaseModel, Extra, Field

ALPHANUMERIC_SPACES_AND_UNDERSCORES = r"^[a-zA-Z0-9 _]*$"


class ProductTeamPathParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = Field(...)


class CreateCpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)


class CpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)


class CreateProductTeamIncomingParams(BaseModel, extra=Extra.forbid):
    ods_code: str = Field(...)
    name: str = Field(...)
    keys: list[ProductTeamKey] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        # Deduplicate the list of keys
        self.keys = list(
            {frozenset(key.dict().items()): key for key in self.keys}.values()
        )


class CreateDeviceReferenceDataIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)


class CreateDeviceReferenceMessageSetsDataParams(BaseModel, extra=Extra.forbid):
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_MHS_MESSAGE_SETS], list[dict]
    ] = Field(default_factory=lambda: defaultdict(list))


class CreateDeviceReferenceAdditionalInteractionsDataParams(
    BaseModel, extra=Extra.forbid
):
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_AS_ADDITIONAL_INTERACTIONS], list[dict]
    ] = Field(default_factory=lambda: defaultdict(list))


class DeviceReferenceDataPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    device_reference_data_id: str = Field(...)


class QuestionnairePathParams(BaseModel, extra=Extra.forbid):

    # NB: questionnaire_id maps onto the domain field Questionnaire.name
    questionnaire_id: str = Field(regex=ALPHANUMERIC_SPACES_AND_UNDERSCORES)


class CreateDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)


class SpineMhsQuestionnaireRsponse(BaseModel):
    __root__: list[dict] = Field(min_items=1, max_items=1)


class SpineAsQuestionnaireResponse(BaseModel):
    __root__: list[dict] = Field(min_items=1, max_items=1)


class CreateMhsDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_MHS], SpineMhsQuestionnaireRsponse
    ] = Field(...)


class CreateAsDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = AS_DEVICE_NAME
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_AS], SpineAsQuestionnaireResponse
    ] = Field(...)


class DevicePathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    device_id: str = Field(...)
