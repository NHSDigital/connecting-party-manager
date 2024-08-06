import json
import os
from unittest import mock

import pytest
from domain.core.device.v2 import DeviceType as DeviceTypeV2
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.questionnaire.v2 import Questionnaire
from domain.core.root.v2 import Root
from domain.repository.device_repository.mock_search_responses.mock_responses import (
    device_5NR_result,
)
from domain.repository.device_repository.v2 import DeviceRepository
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.response_assertions import _response_assertions
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name-a"
    )
    return product_team


def _create_device(device, product_team):
    cpmdevice = product_team.create_device(
        name=device["device_name"], device_type=DeviceTypeV2.PRODUCT
    )
    cpmdevice.add_key(key_value=device["device_key"], key_type=DeviceKeyType.PRODUCT_ID)

    questionnaire = Questionnaire(name=f"spine_{device['device_name']}", version=1)
    questionnaire.add_question(
        name="nhs_as_svc_ia", answer_types=(str,), mandatory=True, multiple=True
    )
    questionnaire.add_question(
        name="nhs_as_client", answer_types=(str,), mandatory=True
    )
    response = [
        {"nhs_as_client": ["5NR"]},
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
    questionnaire_response = questionnaire.respond(responses=response)
    cpmdevice.add_questionnaire_response(questionnaire_response=questionnaire_response)
    cpmdevice.add_tag(
        nhs_as_client="5NR", nhs_as_svc_ia="urn:nhs:names:services:mm:PORX_IN090101UK31"
    )
    return cpmdevice


@pytest.mark.parametrize(
    "params, device, expected_body",
    [
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
            device_5NR_result,
        ),
        # (
        #     {
        #         "nhs_as_client": "5NR",
        #         "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
        #         "nhs_mhs_manufacturer_org": "LSP02",
        #     },
        #     device_5NR_result,
        # ),
    ],
)
def test_index(params, device, expected_body):
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
        from api.searchSdsDevice.index import cache as device_cache
        from api.searchSdsDevice.index import handler as device_handler

        device_cache["DYNAMODB_CLIENT"] = client

        device_repo = DeviceRepository(
            table_name=device_cache["DYNAMODB_TABLE"],
            dynamodb_client=device_cache["DYNAMODB_CLIENT"],
        )
        device_repo.write(cpmdevice)

        result = device_handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    result_body = json_loads(result["body"])

    expected_result = {
        "statusCode": 200,
        "body": json.dumps(expected_body),
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(json.dumps(expected_body))),
            "Version": "1",
            "Location": None,
            "Host": "foo.co.uk",
        },
    }
    _response_assertions(
        result=result,
        expected=expected_result,
        check_body=True,
        check_content_length=True,
    )


@pytest.mark.parametrize(
    "params, error, statusCode",
    [
        ({"nhs_as_client": "5NR"}, "MISSING_VALUE", 400),
        (
            {
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "nhs_mhs_manufacturer_org": "LSP02",
            },
            "MISSING_VALUE",
            400,
        ),
        ({"nhs_mhs_manufacturer_org": "LSP02"}, "MISSING_VALUE", 400),
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "foo": "bar",
            },
            "VALIDATION_ERROR",
            400,
        ),
    ],
)
def test_filter_errors(params, error, statusCode):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsDevice.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client
        result = handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    assert result["statusCode"] == statusCode
    assert error in result["body"]
