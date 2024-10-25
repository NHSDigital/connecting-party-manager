from domain.core.product_team_key import ProductTeamKey
from pydantic import BaseModel, Extra, Field

ALPHANUMERIC_SPACES_AND_UNDERSCORES = r"^[a-zA-Z0-9 _]*$"


class ProductTeamPathParams(BaseModel, extra=Extra.forbid):
    product_team_id: str = Field(...)


class CreateCpmProductIncomingParams(BaseModel, extra=Extra.forbid):
    product_name: str = Field(...)


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


class CreateDeviceReferenceDataParams(BaseModel, extra=Extra.forbid):
    name: str = Field(...)


class DeviceReferenceDataPathParams(BaseModel, extra=Extra.forbid):
    product_id: str = Field(...)
    product_team_id: str = Field(...)
    device_reference_data_id: str = Field(...)


class QuestionnairePathParams(BaseModel, extra=Extra.forbid):

    # NB: questionnaire_id maps onto the domain field Questionnaire.name
    questionnaire_id: str = Field(regex=ALPHANUMERIC_SPACES_AND_UNDERSCORES)
