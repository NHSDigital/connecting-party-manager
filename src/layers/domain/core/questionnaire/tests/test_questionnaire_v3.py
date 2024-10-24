import json

import pytest
from domain.core.enum import Status
from domain.core.questionnaire.v3 import Questionnaire
from domain.core.timestamp import now
from jsonschema import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError as PydanticValidationError

VALID_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "size": {
            "type": "number",
            "minimum": 1,
            "maximum": 14,
        },
        "colour": {
            "type": "string",
            "enum": ["black", "white"],
        },
        "brand": {"type": "string"},  # not required
    },
    "required": ["size", "colour"],
    "additionalProperties": False,
}

INVALID_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "a-field": {
            "type": "not-a-type",
        }
    },
    "required": ["a-field"],
}


@pytest.mark.parametrize(
    "data",
    [
        {"size": 1, "colour": "black"},
        {"size": 14, "colour": "white"},
        {"size": 7, "colour": "white", "brand": "something"},
    ],
)
def test_schema_validation_pass(data):
    questionnaire = Questionnaire(
        name="foo", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )
    response = questionnaire.validate(data=data)
    assert response.name == "foo"
    assert response.version == "1"
    assert response.data == data
    assert response.status is Status.ACTIVE
    assert response.created_on.date() == now().date()
    assert response.updated_on is None
    assert response.deleted_on is None


@pytest.mark.parametrize(
    "data",
    [
        {"size": 1, "colour": "red"},
        {"size": "not a number", "colour": "white"},
        {
            "size": 7,
            "colour": "white",
            "brand": "something",
            "unknown_field": "foo",
        },
    ],
)
def test_schema_validation_fail(data):
    questionnaire = Questionnaire(
        name="foo", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )
    with pytest.raises(JsonSchemaValidationError):
        questionnaire.validate(data=data)


@pytest.mark.parametrize(
    "schema",
    [
        {},
        INVALID_SCHEMA,
    ],
)
def test_invalid_schema(schema):
    with pytest.raises(PydanticValidationError):
        Questionnaire(name="name", version="123", json_schema=json.dumps(schema))
