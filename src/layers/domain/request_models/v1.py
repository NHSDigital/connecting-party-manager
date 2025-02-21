from collections import defaultdict
from typing import Literal

from domain.core.enum import Environment
from domain.core.product_team_key import ProductTeamKey
from domain.repository.questionnaire_repository import QuestionnaireInstance
from pydantic import BaseModel, Extra, Field, root_validator, validator

ALPHANUMERIC_SPACES_AND_UNDERSCORES = r"^[a-zA-Z0-9 _]*$"
ALLOWED_PRODUCT_SEARCH_PARAMS = (
    "product_team_id",
    "organisation_code",
)


class ProductTeamPathParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = Field(...)

    @root_validator(pre=True)
    def ignore_env(cls, values):
        values.pop("environment", None)
        return values


class CreateCpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ensure this value has at least 1 characters")
        return v


class CpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)

    @root_validator(pre=True)
    def ignore_env(cls, values):
        values.pop("environment", None)
        return values


class SubCpmProductPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    environment: Environment


class CreateProductTeamIncomingParams(BaseModel, extra=Extra.forbid):
    ods_code: str = Field(...)
    name: str = Field(...)
    keys: list[ProductTeamKey] = Field(default_factory=list)

    @validator("name")
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ensure this value has at least 1 characters")
        return v

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
    environment: Environment
    device_reference_data_id: str = Field(...)


class QuestionnairePathParams(BaseModel, extra=Extra.forbid):

    # NB: questionnaire_id maps onto the domain field Questionnaire.name
    questionnaire_id: str = Field(regex=ALPHANUMERIC_SPACES_AND_UNDERSCORES)


class CreateDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)


class SpineAsQuestionnaireResponse(BaseModel):
    __root__: list[dict] = Field(min_items=1, max_items=1)


class CreateMhsDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_MHS], list[dict]
    ] = Field(...)


class CreateAsDeviceIncomingParams(BaseModel, extra=Extra.forbid):
    questionnaire_responses: dict[
        Literal[QuestionnaireInstance.SPINE_AS], SpineAsQuestionnaireResponse
    ] = Field(...)


class DevicePathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    environment: Environment
    device_id: str = Field(...)


class SearchProductQueryParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = None
    organisation_code: str = None

    @root_validator
    def check_filters(cls, values: dict):
        # Count the number of non-null parameters
        non_empty_params = [
            param for param in values.values() if param is not None and param != 0
        ]

        if len(non_empty_params) != 1:
            raise ValueError(
                f"Please provide exactly one valid query parameter: {ALLOWED_PRODUCT_SEARCH_PARAMS}."
            )

        return values

    def get_non_null_params(self):
        return self.dict(exclude_none=True)
