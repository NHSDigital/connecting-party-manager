import json
import os
from unittest import mock

import pytest
from domain.core.device import DeviceStatus
from domain.core.device_key import DeviceKeyType
from domain.core.questionnaire import Questionnaire, QuestionnaireResponse
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions
from test_helpers.uuid import consistent_uuid

from ..src.data.response import devices, endpoints

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name"
    )
    return product_team


def _create_device(device, product_team):
    cpmdevice = product_team.create_device(
        name=device["device_name"],
        device_type=device["device_type"],
        status=DeviceStatus(device["status"]),
    )
    cpmdevice.add_key(key_type=DeviceKeyType.PRODUCT_ID, key=device["device_key"])

    questionnaire = Questionnaire(name=f"spine_{device['device_name']}", version=1)
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
    cpmdevice.add_questionnaire_response(questionnaire_response=questionnaire_response)
    return cpmdevice


def _create_expected_device(
    collection_id, collection_url, product_id, device_name, device_type, device_key
):
    return {
        "resourceType": "Bundle",
        "id": collection_id,
        "total": 2,
        "link": [{"relation": "self", "url": collection_url}],
        "type": "collection",
        "entry": [
            {
                "fullUrl": collection_url,
                "resource": {
                    "resourceType": "Device",
                    "deviceName": [
                        {
                            "name": device_name,
                            "type": "user-friendly-name",
                        }
                    ],
                    "definition": {
                        "identifier": {
                            "system": "connecting-party-manager/device-type",
                            "value": device_type,
                        }
                    },
                    "identifier": [
                        {
                            "system": "connecting-party-manager/product_id",
                            "value": device_key,
                        }
                    ],
                    "owner": {
                        "identifier": {
                            "system": "connecting-party-manager/product-team-id",
                            "value": product_id,
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
                "subject": {"reference": collection_url},
                # "authored": "<dateTime>",
                "author": {"reference": f"https://foo.co.uk/Organization/{product_id}"},
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


@pytest.mark.parametrize(
    "version, device",
    [
        (
            "1",
            {
                "device_key": "P.AAA-CCC",
                "device_name": "device-name-a",
                "device_type": "product",
                "status": "active",
            },
        ),
        (
            "1",
            {
                "device_key": "P.CCC-DDD",
                "device_name": "device-name-b",
                "device_type": "product",
                "status": "inactive",
            },
        ),
        (
            "1",
            {
                "device_key": "P.DDD-EEE",
                "device_name": "device-name-c",
                "device_type": "endpoint",
                "status": "active",
            },
        ),
        (
            "1",
            {
                "device_key": "P.EEE-FFF",
                "device_name": "device-name-d",
                "device_type": "endpoint",
                "status": "inactive",
            },
        ),
    ],
)
def test_index(version, device):
    product_team = _create_org()
    cpmdevice = _create_device(device=device, product_team=product_team)

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
        device_repo.write(entity=cpmdevice)

        result = handler(
            event={
                "headers": {"version": version},
                "queryStringParameters": {"device_type": device["device_type"]},
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    result_body = json_loads(result["body"])
    result_id = result_body.get("id")

    expected_result = json.dumps(
        {
            "resourceType": "Bundle",
            "id": result_id,
            "total": 0,
            "link": [
                {
                    "relation": "self",
                    "url": f"https://foo.co.uk/Device?device_type={device['device_type']}",
                }
            ],
            "type": "searchset",
            "entry": [],
        }
    )

    if device["status"] == "active":
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
                        "url": f"https://foo.co.uk/Device?device_type={device['device_type']}",
                    }
                ],
                "type": "searchset",
                "entry": [
                    _create_expected_device(
                        result_collection_id,
                        result_collection_url,
                        result_product_id,
                        device["device_name"],
                        device["device_type"],
                        device["device_key"],
                    )
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


@pytest.mark.parametrize(
    "version, devices, device_type, expected_device",
    [
        (
            "1",
            [
                {
                    "device_key": "P.AAA-CCC",
                    "device_name": "device-name-a",
                    "device_type": "product",
                    "status": "active",
                },
                {
                    "device_key": "P.CCC-DDD",
                    "device_name": "device-name-b",
                    "device_type": "product",
                    "status": "inactive",
                },
                {
                    "device_key": "P.DDD-EEE",
                    "device_name": "device-name-c",
                    "device_type": "endpoint",
                    "status": "active",
                },
                {
                    "device_key": "P.EEE-FFF",
                    "device_name": "device-name-d",
                    "device_type": "endpoint",
                    "status": "inactive",
                },
            ],
            "product",
            0,
        ),
        (
            "1",
            [
                {
                    "device_key": "P.AAA-CCC",
                    "device_name": "device-name-a",
                    "device_type": "product",
                    "status": "active",
                },
                {
                    "device_key": "P.CCC-DDD",
                    "device_name": "device-name-b",
                    "device_type": "product",
                    "status": "inactive",
                },
                {
                    "device_key": "P.DDD-EEE",
                    "device_name": "device-name-c",
                    "device_type": "endpoint",
                    "status": "active",
                },
                {
                    "device_key": "P.EEE-FFF",
                    "device_name": "device-name-d",
                    "device_type": "endpoint",
                    "status": "inactive",
                },
            ],
            "endpoint",
            2,
        ),
    ],
)
def test_index_active_devices(version, devices, device_type, expected_device):
    product_team = _create_org()
    cpmdevices = []
    for device in devices:
        cpmdevices.append(_create_device(device=device, product_team=product_team))

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
        for cpmdevice in cpmdevices:
            device_repo.write(entity=cpmdevice)

        result = handler(
            event={
                "headers": {"version": version},
                "queryStringParameters": {"device_type": device_type},
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
                    "url": f"https://foo.co.uk/Device?device_type={devices[expected_device]['device_type']}",
                }
            ],
            "type": "searchset",
            "entry": [
                _create_expected_device(
                    result_collection_id,
                    result_collection_url,
                    result_product_id,
                    devices[expected_device]["device_name"],
                    devices[expected_device]["device_type"],
                    devices[expected_device]["device_key"],
                )
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


@pytest.mark.parametrize(
    "version, devices, device_type, expected_device_a, expected_device_b",
    [
        (
            "1",
            [
                {
                    "device_key": "P.AAA-CCC",
                    "device_name": "device-name-a",
                    "device_type": "product",
                    "status": "active",
                },
                {
                    "device_key": "P.CCC-DDD",
                    "device_name": "device-name-b",
                    "device_type": "product",
                    "status": "active",
                },
                {
                    "device_key": "P.DDD-EEE",
                    "device_name": "device-name-c",
                    "device_type": "product",
                    "status": "inactive",
                },
                {
                    "device_key": "P.EEE-FFF",
                    "device_name": "device-name-d",
                    "device_type": "endpoint",
                    "status": "active",
                },
                {
                    "device_key": "P.FFF-GGG",
                    "device_name": "device-name-e",
                    "device_type": "endpoint",
                    "status": "inactive",
                },
            ],
            "product",
            0,
            1,
        ),
        (
            "1",
            [
                {
                    "device_key": "P.AAA-CCC",
                    "device_name": "device-name-a",
                    "device_type": "product",
                    "status": "active",
                },
                {
                    "device_key": "P.CCC-DDD",
                    "device_name": "device-name-b",
                    "device_type": "product",
                    "status": "inactive",
                },
                {
                    "device_key": "P.DDD-EEE",
                    "device_name": "device-name-c",
                    "device_type": "endpoint",
                    "status": "active",
                },
                {
                    "device_key": "P.EEE-FFF",
                    "device_name": "device-name-d",
                    "device_type": "endpoint",
                    "status": "active",
                },
                {
                    "device_key": "P.FFF-GGG",
                    "device_name": "device-name-e",
                    "device_type": "endpoint",
                    "status": "inactive",
                },
            ],
            "endpoint",
            2,
            3,
        ),
    ],
)
def test_index_multiple_active_devices(
    version, devices, device_type, expected_device_a, expected_device_b
):
    product_team = _create_org()
    cpmdevices = []
    for device in devices:
        cpmdevices.append(_create_device(device=device, product_team=product_team))

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
        for cpmdevice in cpmdevices:
            device_repo.write(entity=cpmdevice)

        result = handler(
            event={
                "headers": {"version": version},
                "queryStringParameters": {"device_type": device_type},
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    result_body = json_loads(result["body"])
    result_id = result_body.get("id")
    result_collection_id_a = result_body["entry"][0]["id"]
    result_collection_url_a = result_body["entry"][0]["link"][0]["url"]
    result_collection_id_b = result_body["entry"][1]["id"]
    result_collection_url_b = result_body["entry"][1]["link"][0]["url"]
    result_product_id_a = result_body["entry"][0]["entry"][0]["resource"]["owner"][
        "identifier"
    ]["value"]
    result_product_id_b = result_body["entry"][1]["entry"][0]["resource"]["owner"][
        "identifier"
    ]["value"]

    device_a_name = devices[expected_device_a]["device_name"]
    device_a_type = devices[expected_device_a]["device_type"]
    device_a_key = devices[expected_device_a]["device_key"]
    device_b_name = devices[expected_device_b]["device_name"]
    device_b_type = devices[expected_device_b]["device_type"]
    device_b_key = devices[expected_device_b]["device_key"]

    first_device = result_body["entry"][0]["entry"][0]["resource"]["deviceName"][0][
        "name"
    ]

    if first_device != "device-name-a" and first_device != "device-name-c":
        device_a_name, device_b_name = device_b_name, device_a_name
        device_a_type, device_b_type = device_b_type, device_a_type
        device_a_key, device_b_key = device_b_key, device_a_key

    device_a = _create_expected_device(
        result_collection_id_a,
        result_collection_url_a,
        result_product_id_a,
        device_a_name,
        device_a_type,
        device_a_key,
    )

    device_b = _create_expected_device(
        result_collection_id_b,
        result_collection_url_b,
        result_product_id_b,
        device_b_name,
        device_b_type,
        device_b_key,
    )

    entries = [device_a, device_b]

    expected_result = json.dumps(
        {
            "resourceType": "Bundle",
            "id": result_id,
            "total": 2,
            "link": [
                {
                    "relation": "self",
                    "url": f"https://foo.co.uk/Device?device_type={devices[expected_device_a]['device_type']}",
                }
            ],
            "type": "searchset",
            "entry": entries,
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


@pytest.mark.parametrize(
    "version, device",
    [
        (
            "1",
            {
                "device_type": "product",
            },
        ),
        (
            "1",
            {
                "device_type": "endpoint",
            },
        ),
        (
            "1",
            {"device_type": "product"},
        ),
        (
            "1",
            {"device_type": "endpoint"},
        ),
    ],
)
def test_mock_is_returned(version, device):
    from api.searchDevice.index import handler

    result = handler(
        event={
            "headers": {"version": version},
            "queryStringParameters": {
                "device_type": device["device_type"],
                "use_mock": "true",
            },
            "multiValueHeaders": {"Host": ["foo.co.uk"]},
        }
    )
    result_body = json_loads(result["body"])
    result_id = result_body.get("id")

    expected_result = json.dumps(
        {"product": devices, "endpoint": endpoints}.get(
            device["device_type"].lower(), {}
        )
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
