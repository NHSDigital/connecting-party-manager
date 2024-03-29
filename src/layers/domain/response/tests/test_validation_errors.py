import json

import pytest
from domain.response.validation_errors import (
    InboundJSONDecodeError,
    InboundValidationError,
    mark_json_decode_errors_as_inbound,
    mark_validation_errors_as_inbound,
    parse_validation_error,
)
from event.json import json_loads
from pydantic import BaseModel, ValidationError


class MyNestedModel(BaseModel):
    field_1: str
    field_2: bool


class MyModel(BaseModel):
    top_field: float
    nested_models: list[MyNestedModel]


def _get_validation_error(model_params: dict) -> ValidationError:
    validation_error = None
    try:
        MyModel(**model_params)
    except ValidationError as _validation_error:
        validation_error = _validation_error
    else:
        raise ValueError("These model parameters should have failed!")
    return validation_error


@pytest.mark.parametrize(
    ("model_params", "expected_path_error_mapping"),
    [
        (
            # Every field is bad
            {
                "top_field": "not a float!",
                "nested_models": [
                    {
                        "field_1": {"this is a set, not a string!"},
                        "field_2": "not a bool!",
                    }
                ],
            },
            {
                "MyModel.nested_models.0.field_1": "str type expected",
                "MyModel.nested_models.0.field_2": "value could not be parsed to a boolean",
                "MyModel.top_field": "value is not a valid float",
            },
        ),
        (
            # One field is bad
            {
                "top_field": 123.4,
                "nested_models": [
                    {
                        "field_1": "abc",
                        "field_2": "bad field!",
                    }
                ],
            },
            {
                "MyModel.nested_models.0.field_2": "value could not be parsed to a boolean",
            },
        ),
    ],
)
def test_parse_validation_error(model_params, expected_path_error_mapping: dict):
    validation_error = _get_validation_error(model_params=model_params)
    error_items = parse_validation_error(validation_error=validation_error)
    path_error_mapping = {error_item.path: error_item.msg for error_item in error_items}
    assert path_error_mapping == expected_path_error_mapping


def _get_inbound_validation_error():
    @mark_validation_errors_as_inbound
    def my_function():
        MyModel(**{"field": "bad data!"})

    validation_error = None
    try:
        my_function()
    except ValidationError as _validation_error:
        validation_error = _validation_error
    else:
        raise ValueError("These model parameters should have failed!")
    return validation_error


def test_mark_validation_errors_as_inbound():
    validation_error = _get_inbound_validation_error()

    assert type(validation_error) is InboundValidationError


def _get_inbound_json_decode_error():
    @mark_json_decode_errors_as_inbound
    def my_function():
        json_loads("{")

    json_decode_error = None
    try:
        my_function()
    except json.JSONDecodeError as _json_decode_error:
        json_decode_error = _json_decode_error
    else:
        raise ValueError("This json str should have failed!")
    return json_decode_error


def test_mark_json_decode_errors_as_inbound():
    json_decode_error = _get_inbound_json_decode_error()

    assert type(json_decode_error) is InboundJSONDecodeError
    assert (
        str(json_decode_error)
        == "Invalid JSON body was provided: line 1 column 2 (char 1)"
    )
