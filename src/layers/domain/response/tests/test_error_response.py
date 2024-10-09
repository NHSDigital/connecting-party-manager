import pytest
from api_utils.versioning.errors import VersionException
from domain.ods import InvalidOdsCodeError
from domain.response.coding import SpineCoding
from domain.response.error_response import ErrorResponse
from domain.response.validation_errors import mark_validation_errors_as_inbound
from event.status.errors import StatusNotOk
from pydantic import Extra, ValidationError


@pytest.mark.parametrize(
    "exception", [InvalidOdsCodeError, VersionException, StatusNotOk]
)
def test_error_response_from_known_exception(exception: type[Exception]):
    error_response = ErrorResponse.from_exception(exception("oops"))
    (error_item,) = error_response.errors
    assert isinstance(error_item.code, SpineCoding)
    assert len(error_item.message) > 0


@pytest.mark.parametrize("exception", [ValueError, TypeError])
def test_error_response_from_unknown_exception(exception: type[Exception]):
    error_response = ErrorResponse.from_exception(exception=exception("oops"))
    (error_item,) = error_response.errors
    assert error_item.code == SpineCoding.SERVICE_ERROR
    assert error_item.message == "oops"


@pytest.mark.parametrize(
    ["model_kwargs", "expected_error"],
    (
        [
            dict(number="not a number"),
            {
                "errors": [
                    {
                        "code": SpineCoding.SERVICE_ERROR,
                        "message": "MyModel.number: value is not a valid integer",
                    },
                    {
                        "code": SpineCoding.SERVICE_ERROR,
                        "message": "MyModel.another_number: field required",
                    },
                ]
            },
        ],
        [
            dict(number=123, another_number="not a number"),
            {
                "errors": [
                    {
                        "code": SpineCoding.SERVICE_ERROR,
                        "message": "MyModel.another_number: value is not a valid integer",
                    }
                ]
            },
        ],
        [
            dict(number=123, unknown_value="oops"),
            {
                "errors": [
                    {
                        "code": SpineCoding.SERVICE_ERROR,
                        "message": "MyModel.another_number: field required",
                    },
                    {
                        "code": SpineCoding.SERVICE_ERROR,
                        "message": "MyModel.unknown_value: extra fields not permitted",
                    },
                ]
            },
        ],
    ),
)
def test_error_response_from_external_validation_error(
    model_kwargs: dict, expected_error: dict
):
    from pydantic import BaseModel

    class MyModel(BaseModel, extra=Extra.forbid):
        number: int
        another_number: int

    try:
        MyModel(**model_kwargs)
    except ValidationError as e:
        exception = e

    error_response = ErrorResponse.from_validation_error(exception=exception)
    assert error_response.dict() == expected_error


def test_error_response_from_inbound_validation_error():
    from pydantic import BaseModel

    class MyModel(BaseModel, extra=Extra.forbid):
        number: int
        another_number: int

        @classmethod
        @mark_validation_errors_as_inbound
        def make(cls, **kwargs):
            return cls(**kwargs)

    try:
        MyModel.make(number="not a number", unknown_value="oops")
    except ValidationError as e:
        exception = e

    error_response = ErrorResponse.from_validation_error(exception=exception)
    assert error_response.dict() == {
        "errors": [
            {
                "code": SpineCoding.VALIDATION_ERROR,
                "message": "MyModel.number: value is not a valid integer",
            },
            {
                "code": SpineCoding.MISSING_VALUE,
                "message": "MyModel.another_number: field required",
            },
            {
                "code": SpineCoding.VALIDATION_ERROR,
                "message": "MyModel.unknown_value: extra fields not permitted",
            },
        ]
    }
