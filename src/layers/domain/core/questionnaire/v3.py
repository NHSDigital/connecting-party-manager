from datetime import datetime
from uuid import UUID, uuid4

import jsonschema
from domain.core.base import BaseModel
from domain.core.timestamp import now
from pydantic import Field, Json, validator


class Questionnaire(BaseModel):
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
        jsonschema.validate(instance=data, schema=self.json_schema)
        return QuestionnaireResponse(
            questionnaire_name=self.name, questionnaire_version=self.version, data=data
        )


class QuestionnaireResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    questionnaire_name: str
    questionnaire_version: str
    data: dict
    created_on: datetime = Field(default_factory=now)
