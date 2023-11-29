import json
from http import HTTPStatus

import pytest
from event.response.render_response import render_response
from event.response.response_matrix import SUCCESS_STATUSES
from event.response.tests.test_validation_errors import (
    _get_inbound_validation_error,
    _get_validation_error,
)

NON_SUCCESS_STATUSES = set(HTTPStatus._member_map_.values()) - SUCCESS_STATUSES


def test_render_response_of_json_serialisable():
    aws_lambda_response = render_response(response={"dict": "of things"})
    assert aws_lambda_response.dict() == {
        "statusCode": HTTPStatus.OK,
        "body": '{"dict": "of things"}',
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": 21,
        },
    }


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

    assert aws_lambda_response.dict() == {
        "statusCode": 201,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


@pytest.mark.parametrize("http_status", NON_SUCCESS_STATUSES)
def test_render_response_of_non_success_http_status(http_status: HTTPStatus):
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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": f"HTTP Status '{http_status.value}' should not be explicitly returned from the API. For non-2XX statuses we should raise exceptions for control flow of API failures. Any 2XX statuses should be added to SUCCESS_STATUSES.",
                }
            ],
        }
    )
    aws_lambda_response = render_response(response=http_status, id="foo")

    assert aws_lambda_response.dict() == {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


def test_render_response_of_non_json_serialisable():
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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "Object of type object is not JSON serializable",
                }
            ],
        }
    )

    aws_lambda_response = render_response(object(), id="foo")
    assert aws_lambda_response.dict() == {
        "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


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
    assert aws_lambda_response.dict() == {
        "statusCode": HTTPStatus.OK,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


def test_render_response_of_blank_exception():
    aws_lambda_response = render_response(response=Exception(), id="foo")
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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "An exception of type 'Exception' was raised with no message",
                }
            ],
        }
    )
    assert aws_lambda_response.dict() == {
        "statusCode": 500,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


def test_render_response_of_general_exception():
    aws_lambda_response = render_response(response=Exception("oops"), id="foo")
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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "oops",
                }
            ],
        }
    )
    assert aws_lambda_response.dict() == {
        "statusCode": 500,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "value is not a valid float",
                    "expression": ["MyModel.top_field"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "str type expected",
                    "expression": ["MyModel.nested_models.0.field_1"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "SERVICE_ERROR",
                                "display": "Service error",
                            }
                        ]
                    },
                    "diagnostics": "value could not be parsed to a boolean",
                    "expression": ["MyModel.nested_models.0.field_2"],
                },
            ],
        }
    )
    assert aws_lambda_response.dict() == {
        "statusCode": 500,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }


def test_render_response_of_internal_validation_error():
    validation_error = _get_inbound_validation_error()
    aws_lambda_response = render_response(response=validation_error, id="foo")
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
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["MyModel.top_field"],
                },
                {
                    "severity": "error",
                    "code": "processing",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
                                "code": "MISSING_VALUE",
                                "display": "Missing value",
                            }
                        ]
                    },
                    "diagnostics": "field required",
                    "expression": ["MyModel.nested_models"],
                },
            ],
        }
    )
    assert aws_lambda_response.dict() == {
        "statusCode": 400,
        "body": expected_body,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": len(expected_body),
        },
    }
