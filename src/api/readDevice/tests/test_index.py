import json
import os
from unittest import mock

import pytest
from domain.core.device_key import DeviceKeyType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"


def _response_assertion(result, expected):
    assert "statusCode" in result
    assert result["statusCode"] == expected["statusCode"]
    assert "body" in result
    assert "headers" in result
    header_response = result.get("headers", {})
    assert "Content-Type" in header_response
    assert header_response["Content-Type"] == expected["headers"]["Content-Type"]
    assert "Content-Length" in header_response
    assert header_response["Content-Length"] == expected["headers"]["Content-Length"]
    assert "Version" in header_response
    assert header_response["Version"] == expected["headers"]["Version"]
    assert "Location" in header_response
    assert result["body"] == expected["body"]
    assert header_response["Content-Length"] == expected["headers"]["Content-Length"]


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index(version):
    device_key = "P.XXX-YYY"
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    device = product_team.create_device(name="device-name", type="product")
    device.add_key(DeviceKeyType.PRODUCT_ID, device_key)

    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.readDevice.index import handler

        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(entity=device)

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"id": str(device.id)},
            }
        )

    expected_result = json.dumps(
        {
            "resourceType": "Device",
            "deviceName": [{"name": "device-name", "type": "user-friendly-name"}],
            "definition": {
                "identifier": {
                    "system": "connecting-party-manager/device-type",
                    "value": "product",
                }
            },
            "identifier": [
                {"system": "connecting-party-manager/product_id", "value": "P.XXX-YYY"}
            ],
            "owner": {
                "identifier": {
                    "system": "connecting-party-manager/product-team-id",
                    "value": consistent_uuid(1),
                }
            },
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertion(result, expected)


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_device(version):
    with mock_table(TABLE_NAME), mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.readDevice.index import handler

        result = handler(
            event={
                "headers": {"version": version},
                "pathParameters": {"id": "123"},
            }
        )

    expected_result = json.dumps(
        {
            "resourceType": "OperationOutcome",
            "id": app_logger.service_name,
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
                                "code": "RESOURCE_NOT_FOUND",
                                "display": "Resource not found",
                            }
                        ]
                    },
                    "diagnostics": "Could not find object with key '123'",
                }
            ],
        }
    )

    expected = {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertion(result, expected)
