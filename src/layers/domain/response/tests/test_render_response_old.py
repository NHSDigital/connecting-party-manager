import json
from http import HTTPStatus

import pytest
from domain.response.render_response_old import render_response
from domain.response.response_matrix import SUCCESS_STATUSES
from domain.response.tests.test_validation_errors import (
    _get_inbound_validation_error,
    _get_validation_error,
)
from event.json import json_loads

from test_helpers.response_assertions import _response_assertions

NON_SUCCESS_STATUSES = set(HTTPStatus._member_map_.values()) - SUCCESS_STATUSES


def test_render_response_of_json_serialisable():
    aws_lambda_response = render_response(response={"dict": "of things"})
    expected = {
        "statusCode": HTTPStatus.OK,
        "body": '{"dict": "of things"}',
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": "14",
            "Version": "null",
        },
    }
    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


def test_render_response_of_success_http_status_created():
    expected_body = json.dumps(
        {
            "resourceType": "OperationOutcome",
            "id": "foo",
            "meta": {
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "information",
                    "code": "informational",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "RESOURCE_CREATED",
                                "display": "Resource created",
                            }
                        ]
                    },
                    "diagnostics": "Resource created",
                }
            ],
        }
    )

    aws_lambda_response = render_response(response=HTTPStatus.CREATED, id="foo")

    expected = {
        "statusCode": 201,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }

    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


@pytest.mark.parametrize("http_status", NON_SUCCESS_STATUSES)
def test_render_response_of_non_success_http_status(http_status: HTTPStatus):
    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "SERVICE_ERROR",
                    "message": (
                        f"HTTP Status '{http_status.value}' should not be explicitly returned from the API. "
                        "For non-2XX statuses we should raise exceptions for control flow of API failures. "
                        "Any 2XX statuses should be added to SUCCESS_STATUSES."
                    ),
                }
            ],
        }
    )
    aws_lambda_response = render_response(response=http_status, id="foo")

    expected = {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }

    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


def test_render_response_of_non_json_serialisable():
    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "SERVICE_ERROR",
                    "message": "Object of type object is not JSON serializable",
                }
            ],
        }
    )

    aws_lambda_response = render_response(object(), id="foo")
    expected = {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }
    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


@pytest.mark.parametrize(
    ["response", "expected_body"],
    [
        ({"foo": "bar"}, '{"foo": "bar"}'),
        (123, "123"),
        (True, "true"),
        ("aString", '"aString"'),
    ],
)
def test_render_response_of_json_serialisable(response, expected_body):
    aws_lambda_response = render_response(response, id="foo")
    expected = {
        "statusCode": HTTPStatus.OK,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }
    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


def test_render_response_of_blank_exception():
    aws_lambda_response = render_response(response=Exception(), id="foo")
    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "SERVICE_ERROR",
                    "message": "An exception of type 'Exception' was raised with no message",
                }
            ],
        }
    )
    expected = {
        "statusCode": 500,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }
    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


def test_render_response_of_general_exception():
    aws_lambda_response = render_response(response=Exception("oops"), id="foo")
    expected_body = json.dumps(
        {
            "errors": [
                {
                    "code": "SERVICE_ERROR",
                    "message": "oops",
                }
            ],
        }
    )
    expected = {
        "statusCode": 500,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_body)),
            "Version": "null",
        },
    }
    _response_assertions(
        result=aws_lambda_response.dict(),
        expected=expected,
        check_body=True,
        check_content_length=True,
    )


def test_render_response_of_general_validation_error():
    model_inputs = {
        "top_field": "not a float!",
        "nested_models": [
            {
                "field_1": {"this is a set, not a string!"},
                "field_2": "not a bool!",
            }
        ],
    }

    validation_error = _get_validation_error(model_inputs)
    aws_lambda_response = render_response(response=validation_error, id="foo")
    expected_body = {
        "errors": [
            {
                "code": "SERVICE_ERROR",
                "message": "MyModel.top_field: value is not a valid float",
            },
            {
                "code": "SERVICE_ERROR",
                "message": "MyModel.nested_models.0.field_1: str type expected",
            },
            {
                "code": "SERVICE_ERROR",
                "message": "MyModel.nested_models.0.field_2: value could not be parsed to a boolean",
            },
        ],
    }
    body = json_loads(aws_lambda_response.body)
    assert body == expected_body
    assert aws_lambda_response.statusCode == 500
    assert aws_lambda_response.headers.content_length == str(
        len(aws_lambda_response.body)
    )
    assert aws_lambda_response.headers.content_type == "application/json"
    assert aws_lambda_response.headers.version == "null"


def test_render_response_of_internal_validation_error():
    validation_error = _get_inbound_validation_error()
    aws_lambda_response = render_response(response=validation_error, id="foo")
    expected_body = {
        "errors": [
            {
                "code": "MISSING_VALUE",
                "message": "MyModel.top_field: field required",
            },
            {
                "code": "MISSING_VALUE",
                "message": "MyModel.nested_models: field required",
            },
        ],
    }
    body = json_loads(aws_lambda_response.body)
    assert body == expected_body
    assert aws_lambda_response.statusCode == 400
    assert aws_lambda_response.headers.content_length == str(
        len(aws_lambda_response.body)
    )
    assert aws_lambda_response.headers.content_type == "application/json"
    assert aws_lambda_response.headers.version == "null"
