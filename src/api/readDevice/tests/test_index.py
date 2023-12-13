import json
import os
from unittest import mock

import pytest
from nhs_context_logging import app_logger

from test_helpers.dynamodb import mock_table

TABLE_NAME = "hiya"

# Uncomment this once PI-138 is implemented
# @pytest.mark.parametrize(
#     "version",
#     [
#         "1",
#     ],
# )
# def test_index(version):
#     device_id = "XXX-YYY"
#     org = Root.create_ods_organisation(ods_code="ABC")
#     product_team = org.create_product_team(
#         id=consistent_uuid(1), name="product-team-name"
#     )
#     device = product_team.create_device(
#         id=device_id, name="device-name", type="product"
#     )
#     device.add_key(type="product_id", key=device_id)
#     print(device.keys)

#     with mock_table(TABLE_NAME) as client, mock.patch.dict(
#         os.environ,
#         {
#             "DYNAMODB_TABLE": TABLE_NAME,
#             "AWS_DEFAULT_REGION": "eu-west-2",
#         },
#         clear=True,
#     ):
#         from api.readDevice.index import handler

#         device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
#         device_repo.write(entity=device)

#         result = handler(
#             event={
#                 "headers": {"version": version},
#                 "pathParameters": {"id": device_id},
#             }
#         )

#     expected_result = json.dumps(
#         {
#             "resourceType": "Organization",
#             "identifier": [
#                 {
#                     "system": "connecting-party-manager",
#                     "value": device_id,
#                 }
#             ],
#             "name": "product-team-name",
#             "partOf": {
#                 "identifier": {
#                     "system": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations",
#                     "value": "ABC",
#                 }
#             },
#         }
#     )

#     assert result == {
#         "statusCode": 200,
#         "body": expected_result,
#         "headers": {
#             "Content-Length": len(expected_result),
#             "Content-Type": "application/json",
#         },
#     }


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

    assert result == {
        "statusCode": 404,
        "body": expected_result,
        "headers": {
            "Content-Length": len(expected_result),
            "Content-Type": "application/json",
        },
    }
