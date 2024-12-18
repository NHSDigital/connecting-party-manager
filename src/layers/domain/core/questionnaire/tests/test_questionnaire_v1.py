import json

import pytest
from domain.core.questionnaire import (
    Questionnaire,
    QuestionnaireResponseMissingValue,
    QuestionnaireResponseValidationError,
)
from domain.core.timestamp import now
from pydantic import ValidationError

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
    assert response.questionnaire_name == "foo"
    assert response.questionnaire_version == "1"
    assert response.data == data
    assert response.created_on.date() == now().date()


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
    with pytest.raises(QuestionnaireResponseValidationError):
        questionnaire.validate(data=data)


@pytest.mark.parametrize(
    "data",
    [
        {"size": 1},
        {"colour": "white"},
    ],
)
def test_schema_validation_missing_fail(data):
    questionnaire = Questionnaire(
        name="foo", version="1", json_schema=json.dumps(VALID_SCHEMA)
    )
    with pytest.raises(QuestionnaireResponseMissingValue):
        questionnaire.validate(data=data)


@pytest.mark.parametrize(
    "schema",
    [
        INVALID_SCHEMA,
    ],
)
def test_invalid_schema(schema):
    with pytest.raises(ValidationError):
        Questionnaire(name="name", version="123", json_schema=json.dumps(schema))
