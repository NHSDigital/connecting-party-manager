from datetime import datetime
from uuid import UUID, uuid4

import jsonschema
from domain.core.aggregate_root import AggregateRoot
from domain.core.base import BaseModel
from domain.core.error import ConfigurationError
from domain.core.timestamp import now
from pydantic import Field, Json, validator
from sds.epr.constants import SdsFieldName

REQUIRED = "required"


# This will be moved as part of a QuestionnaireInstance refactor
def generate_spine_mhs_fields(response: dict, **kwargs) -> None:
    required_fields = [SdsFieldName.MHS_FQDN]
    missing_fields = [field for field in required_fields if not response.get(field)]
    if missing_fields:
        # use questionnaire instance for questionnaire name?
        raise ConfigurationError(
            f"The following required fields are missing in the response to spine_mhs: {', '.join(missing_fields)}"
        )

    response[str(SdsFieldName.ADDRESS)] = (
        f"https://{response.get(SdsFieldName.MHS_FQDN)}"
    )
    party_key = kwargs.get("party_key")
    response[str(SdsFieldName.PARTY_KEY)] = party_key
    response[str(SdsFieldName.MANAGING_ORGANIZATION)] = party_key.split("-")[0]
    response[str(SdsFieldName.DATE_APPROVED)] = str(now())
    response[str(SdsFieldName.DATE_REQUESTED)] = str(now())
    response[str(SdsFieldName.DATE_DNS_APPROVED)] = str(None)


def generate_spine_mhs_message_sets_fields(response: dict, **kwargs):
    """
    Generates system fields for a given questionnaire response.
    """

    # Ensure required fields for system-generated fields are present
    required_fields = [SdsFieldName.MHS_SN, SdsFieldName.MHS_IN]
    missing_fields = [field for field in required_fields if not response.get(field)]
    if missing_fields:
        raise ConfigurationError(
            f"The following required fields are missing in the response to spine_mhs_message_sets: {', '.join(missing_fields)}"
        )

    # Generate system fields
    response[str(SdsFieldName.INTERACTION_ID)] = (
        f"{response.get(SdsFieldName.MHS_SN)}:{response.get(SdsFieldName.MHS_IN)}"
    )
    party_key = kwargs.get("party_key")
    response[str(SdsFieldName.CPA_ID)] = (
        f"{party_key}:{response[SdsFieldName.INTERACTION_ID]}"
    )
    response[str(SdsFieldName.UNIQUE_IDENTIFIER)] = response[SdsFieldName.CPA_ID]


# Mapping of QuestionnaireInstance to field generation functions
FIELD_GENERATION_STRATEGIES = {
    "spine_mhs": generate_spine_mhs_fields,
    "spine_mhs_message_sets": generate_spine_mhs_message_sets_fields,
}


class QuestionnaireResponseValidationError(Exception): ...


class QuestionnaireResponseMissingValue(Exception): ...


class Questionnaire(AggregateRoot):
    name: str
    version: str
    json_schema: Json

    @validator("json_schema")
    def validate_json_schema(cls, json_schema):
        try:
            jsonschema.Draft7Validator.check_schema(json_schema)
        except jsonschema.SchemaError as err:
            raise ValueError(err.message)
        return json_schema

    def validate(self, data) -> "QuestionnaireResponse":
        try:
            jsonschema.validate(instance=data, schema=self.json_schema)
        except jsonschema.ValidationError as error:
            *_, variable_name = error.schema_path
            exception_type = (
                QuestionnaireResponseMissingValue
                if variable_name == REQUIRED
                else QuestionnaireResponseValidationError
            )
            raise exception_type(
                f"Failed to validate data against '{self.id}': {error.message}"
            )

        return QuestionnaireResponse(
            questionnaire_name=self.name, questionnaire_version=self.version, data=data
        )

    @property
    def id(self) -> str:
        return f"{self.name}/{self.version}"

    @property
    def user_provided_fields(self) -> list[str]:
        """
        Returns a generator object of fields NOT marked as 'system generated' in the JSON schema.
        """
        properties = self.json_schema.get("properties", {})
        return (
            field_name
            for field_name, field_attrs in properties.items()
            if not field_attrs.get("system generated", False)
        )

    @property
    def system_generated_fields(self) -> list[str]:
        """
        Returns a list of fields marked as 'system generated' in the JSON schema.
        """
        properties = self.json_schema.get("properties", {})
        return [
            field_name
            for field_name, field_attrs in properties.items()
            if field_attrs.get("system generated") is True
        ]

    def generate_system_fields(self, response: dict, instance, **kwargs) -> None:
        """
        Delegates system field generation to the appropriate strategy.
        """
        strategy = FIELD_GENERATION_STRATEGIES.get(instance)
        if not strategy:
            raise NotImplementedError(
                f"System field generation is not implemented for {instance}"
            )
        strategy(response, **kwargs)


class QuestionnaireResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    questionnaire_name: str
    questionnaire_version: str
    data: dict
    created_on: datetime = Field(default_factory=now)

    @property
    def questionnaire_id(self) -> str:
        return f"{self.questionnaire_name}/{self.questionnaire_version}"
