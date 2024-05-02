import json
import os
from unittest import mock

import pytest
from domain.core.device_key import DeviceKeyType
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from event.json import json_loads

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

    questionnaire = Questionnaire(name="spine_device", version=1)
    questionnaire.add_question(
        name="nhs_as_svc_ia",
        human_readable_name="Interaction Ids",
        mandatory=True,
        multiple=True,
    )
    response = [
        {
            "nhs_as_svc_ia": [
                "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "urn:nhs:names:services:pdsquery:QUPA_IN000009UK03",
                "urn:nhs:names:services:mm:PORX_IN070101UK31",
                "urn:nhs:names:services:pds:PRPA_IN000203UK03",
                "urn:nhs:names:services:mm:PORX_IN110101UK30",
                "urn:nhs:names:services:pdsquery:QUPA_IN000007UK01",
                "urn:nhs:names:services:pdsquery:QUPA_IN000005UK01",
                "urn:nhs:names:services:mmquery:PRESCRIPTIONSEARCHRESPONSE_SM01",
                "urn:nhs:names:services:mmquery:PORX_IN000006UK99",
                "urn:nhs:names:services:mmquery:PORX_IN999000UK01",
                "urn:nhs:names:services:pds:PRPA_IN000202UK01",
                "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "urn:nhs:names:services:mmquery:PORX_IN999001UK01",
                "urn:nhs:names:services:pdsquery:QUPA_IN000008UK02",
                "urn:nhs:names:services:mmquery:QURX_IN000005UK99",
                "urn:nhs:names:services:pdsquery:QUQI_IN010000UK14",
                "urn:nhs:names:services:mmquery:ExternalPrescriptionQuery_1_0",
                "urn:nhs:names:services:mm:PORX_IN070103UK31",
                "urn:nhs:names:services:mm:PORX_IN080101UK31",
                "urn:nhs:names:services:mmquery:ExternalPrescriptionSearch_1_0",
                "urn:nhs:names:services:mm:MCCI_IN010000UK13",
                "urn:oasis:names:tc:ebxml-msg:service:MessageError",
                "urn:nhs:names:services:mm:PORX_IN100101UK31",
                "urn:nhs:names:services:mm:PORX_IN510101UK31",
                "urn:nhs:names:services:mm:PORX_IN060102UK30",
                "urn:nhs:names:services:mmquery:PRESCRIPTIONSEARCH_SM01",
                "urn:nhs:names:services:mm:PORX_IN132004UK30",
            ]
        },
    ]
    questionnaire_response = QuestionnaireResponse(
        questionnaire=questionnaire, responses=response
    )
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)

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
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    result_body = json_loads(result["body"])
    result_id = result_body.get("id")
    result_collection_id = result_body["entry"][0]["id"]
    result_collection_url = result_body["entry"][0]["link"][0]["url"]
    result_product_id = result_body["entry"][0]["entry"][0]["resource"]["owner"][
        "identifier"
    ]["value"]

    expected_result = json.dumps(
        {
            "resourceType": "Bundle",
            "id": result_id,
            "total": 1,
            "link": [
                {
                    "relation": "self",
                    "url": "https://foo.co.uk/Device?device_type=product",
                }
            ],
            "type": "searchset",
            "entry": [
                {
                    "resourceType": "Bundle",
                    "id": result_collection_id,
                    "total": 1,
                    "link": [{"relation": "self", "url": result_collection_url}],
                    "type": "collection",
                    "entry": [
                        {
                            "fullUrl": result_collection_url,
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
                                        "value": result_product_id,
                                    }
                                },
                            },
                            "search": {"mode": "match"},
                        },
                        {
                            "resourceType": "QuestionnaireResponse",
                            # "identifier": "010057927542",
                            # "questionnaire": "https://cpm.co.uk/Questionnaire/spine_device|v1",
                            "status": "completed",
                            "subject": {"reference": result_collection_url},
                            # "authored": "<dateTime>",
                            "author": {
                                "reference": f"https://foo.co.uk/Organization/{result_product_id}"
                            },
                            "item": [
                                {
                                    "link_id": "nhs_as_svc_ia",
                                    "text": "nhs_as_svc_ia",
                                    "answer": [
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN090101UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN000009UK03"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN070101UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pds:PRPA_IN000203UK03"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN110101UK30"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN000007UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN000005UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:PRESCRIPTIONSEARCHRESPONSE_SM01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:PORX_IN000006UK99"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:PORX_IN999000UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pds:PRPA_IN000202UK01"
                                        },
                                        {
                                            "valueString": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:PORX_IN999001UK01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pdsquery:QUPA_IN000008UK02"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:QURX_IN000005UK99"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:pdsquery:QUQI_IN010000UK14"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:ExternalPrescriptionQuery_1_0"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN070103UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN080101UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:ExternalPrescriptionSearch_1_0"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:MCCI_IN010000UK13"
                                        },
                                        {
                                            "valueString": "urn:oasis:names:tc:ebxml-msg:service:MessageError"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN100101UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN510101UK31"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN060102UK30"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mmquery:PRESCRIPTIONSEARCH_SM01"
                                        },
                                        {
                                            "valueString": "urn:nhs:names:services:mm:PORX_IN132004UK30"
                                        },
                                    ],
                                }
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
            "Content-Type": "application/json",
            "Content-Length": str(len(expected_result)),
            "Version": version,
            "Location": None,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )
