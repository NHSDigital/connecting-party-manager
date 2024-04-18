import json
import os
from unittest import mock

import pytest
from domain.core.device_key import DeviceKeyType
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"


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
        from api.searchDevice.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client

        device_repo = DeviceRepository(table_name=TABLE_NAME, dynamodb_client=client)
        device_repo.write(entity=device)

        result = handler(
            event={
                "headers": {"version": version},
                "queryStringParameters": {"device_type": "product"},
            }
        )

    expected_result = json.dumps(
        {
            "resourceType": "Bundle",
            "id": consistent_uuid(1),
            "type": "searchset",
            "total": 1,
            "link": [{"relation": "self", "url": "https://cpm.co.uk/Device"}],
            "entry": [
                {
                    "resourceType": "Bundle",
                    "id": consistent_uuid(1),
                    "type": "collection",
                    "total": 1,
                    "link": [
                        {
                            "relation": "self",
                            "url": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae",
                        }
                    ],
                    "entry": [
                        {
                            "fullUrl": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae",
                            "resource": {
                                "resourceType": "Device",
                                "deviceName": [
                                    {
                                        "name": "device-name",
                                        "type": "user-friendly-name",
                                    }
                                ],
                                "definition": {
                                    "identifier": {
                                        "system": "connecting-party-manager/device-type",
                                        "value": "product",
                                    }
                                },
                                "identifier": [
                                    {
                                        "system": "connecting-party-manager/product_id",
                                        "value": "P.XXX-YYY",
                                    }
                                ],
                                "owner": {
                                    "identifier": {
                                        "system": "connecting-party-manager/product-team-id",
                                        "value": consistent_uuid(1),
                                    }
                                },
                            },
                        },
                        {
                            "resourceType": "QuestionnaireResponse",
                            "identifier": "010057927542",
                            "questionnaire": "https://cpm.co.uk/Questionnaire/spine_device|v1",
                            "status": "completed",
                            "subject": {
                                "reference": "https://cpm.co.uk/Device/39ae1fe2-dd84-4d9a-af2a-ca0e63f53cae"
                            },
                            "authored": "<dateTime>",
                            "author": {
                                "reference": "https://cpm.co.uk/Organization/ae2ab026-0b53-7e7c-7a65-f0407a6e75f5"
                            },
                            "item": [
                                {
                                    "link_id": "object_class",
                                    "text": "object_class",
                                    "answer": [
                                        {"valueString": "nhsAS"},
                                        {"valueString": "top"},
                                    ],
                                },
                                {
                                    "link_id": "nhs_approver_urp",
                                    "text": "nhs_approver_urp",
                                    "answer": [
                                        {
                                            "valueString": "uniqueIdentifier=562983788547,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                        }
                                    ],
                                },
                                {
                                    "link_id": "nhs_as_client",
                                    "text": "nhs_as_client",
                                    "answer": [{"valueString": "5NR"}],
                                },
                                {
                                    "link_id": "nhs_as_svc_ia",
                                    "text": "nhs_as_svc_ia",
                                    "answer": [
                                        {
                                            "valueString": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment"
                                        },
                                        {
                                            "valueString": "urn:oasis:names:tc:ebxml-msg:service:MessageError"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN020000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN050000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN040000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN030000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:QUPC_IN010000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN050000UK13"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN060000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN080000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:QUQI_IN010000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:QUPC_IN030000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:QUPC_IN010000UK15"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:QUPC_IN040000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN070000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN010000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN110000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN020000UK13"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN010000UK15"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:MCCI_IN010000UK13"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrs:REPC_IN040000UK15"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN040000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrsquery:QUPC_IN030000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrsquery:QUQI_IN010000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:lrsquery:MCCI_IN010000UK13"
                                        },
                                    ],
                                },
                                {
                                    "link_id": "nhs_date_approved",
                                    "text": "nhs_date_approved",
                                    "answer": [
                                        {"valueDateTime": "2008-04-01T13:18:34"}
                                    ],
                                },
                                {
                                    "link_id": "nhs_date_requested",
                                    "text": "nhs_date_requested",
                                    "answer": [
                                        {"valueDateTime": "2008-04-01T12:54:47"}
                                    ],
                                },
                                {
                                    "link_id": "nhs_id_code",
                                    "text": "nhs_id_code",
                                    "answer": [{"valueString": "5NR"}],
                                },
                                {
                                    "link_id": "nhs_mhs_manufacturer_org",
                                    "text": "nhs_mhs_manufacturer_org",
                                    "answer": [{"valueString": "LSP02"}],
                                },
                                {
                                    "link_id": "nhs_mhs_party_key",
                                    "text": "nhs_mhs_party_key",
                                    "answer": [{"valueString": "5NR-801831"}],
                                },
                                {
                                    "link_id": "nhs_product_key",
                                    "text": "nhs_product_key",
                                    "answer": [{"valueInteger": 1113}],
                                },
                                {
                                    "link_id": "nhs_requestor_urp",
                                    "text": "nhs_requestor_urp",
                                    "answer": [
                                        {
                                            "valueString": "uniqueIdentifier=977624345541,uniqueIdentifier=883298590547,uid=503560389549,ou=People,o=nhs"
                                        }
                                    ],
                                },
                                {
                                    "link_id": "nhs_temp_uid",
                                    "text": "nhs_temp_uid",
                                    "answer": [{"valueInteger": 1663}],
                                },
                                {
                                    "link_id": "unique_identifier",
                                    "text": "unique_identifier",
                                    "answer": [{"valueString": "010057927542"}],
                                },
                            ],
                        },
                    ],
                }
            ],
        }
    )

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
            "Location": None,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


# @pytest.mark.parametrize(
#     "version",
#     [
#         "1",
#     ],
# )
# def test_index_no_such_device(version):
#     with mock_table(TABLE_NAME), mock.patch.dict(
#         os.environ,
#         {
#             "DYNAMODB_TABLE": TABLE_NAME,
#             "AWS_DEFAULT_REGION": "eu-west-2",
#         },
#         clear=True,
#     ):
#         from api.readDevice.index import handler

#         result = handler(
#             event={
#                 "headers": {"version": version},
#                 "pathParameters": {"id": "123"},
#             }
#         )

#     expected_result = json.dumps(
#         {
#             "resourceType": "OperationOutcome",
#             "id": app_logger.service_name,
#             "meta": {
#                 "profile": [
#                     "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome"
#                 ]
#             },
#             "issue": [
#                 {
#                     "severity": "error",
#                     "code": "processing",
#                     "details": {
#                         "coding": [
#                             {
#                                 "system": "https://fhir.nhs.uk/StructureDefinition/NHSDigital-OperationOutcome",
#                                 "code": "RESOURCE_NOT_FOUND",
#                                 "display": "Resource not found",
#                             }
#                         ]
#                     },
#                     "diagnostics": "Could not find object with key '123'",
#                 }
#             ],
#         }
#     )

#     expected = {
#         "statusCode": 404,
#         "body": expected_result,
#         "headers": {
#             "Content-Length": str(len(expected_result)),
#             "Content-Type": "application/json",
#             "Version": version,
#             "Location": None,
#         },
#     }
#     _response_assertions(
#         result=result, expected=expected, check_body=True, check_content_length=True
#     )
