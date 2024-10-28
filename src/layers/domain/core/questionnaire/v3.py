from datetime import datetime
from uuid import UUID, uuid4

import jsonschema
from domain.core.aggregate_root import AggregateRoot
from domain.core.base import BaseModel
from domain.core.timestamp import now
from pydantic import Field, Json, validator

REQUIRED = "required"


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


class QuestionnaireResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    questionnaire_name: str
    questionnaire_version: str
    data: dict
    created_on: datetime = Field(default_factory=now)

    @property
    def questionnaire_id(self) -> str:
        return f"{self.questionnaire_name}/{self.questionnaire_version}"
