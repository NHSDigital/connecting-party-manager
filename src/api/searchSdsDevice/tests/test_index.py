import os
from unittest import mock

import pytest
from domain.core.device.v2 import DeviceType as DeviceTypeV2
from domain.core.device_key.v1 import DeviceKeyType
from domain.core.questionnaire.v2 import Questionnaire
from domain.core.root.v2 import Root
from domain.repository.device_repository.v2 import DeviceRepository
from event.aws.client import dynamodb_client
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output
from test_helpers.uuid import consistent_uuid

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name-a"
    )
    return product_team


def _create_device(device, product_team, params):
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
        {"nhs_as_client": [params["nhs_as_client"]]},
        {"nhs_as_svc_ia": [params["nhs_as_svc_ia"]]},
    ]
    questionnaire_response = questionnaire.respond(responses=response)
    cpmdevice.add_questionnaire_response(questionnaire_response=questionnaire_response)
    cpmdevice.add_tag(
        nhs_as_client=params["nhs_as_client"], nhs_as_svc_ia=params["nhs_as_svc_ia"]
    )
    return cpmdevice


@pytest.mark.integration
@pytest.mark.parametrize(
    "params, device",
    [
        (
            {
                "nhs_as_client": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
    ],
)
def test_index(params, device):
    product_team = _create_org()
    cpmdevice = _create_device(device=device, product_team=product_team, params=params)

    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
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

    assert result["statusCode"] == 200

    for result in result_body:
        assert result["name"] == device["device_name"]
        for key in result["keys"]:
            assert key["key_value"] == device["device_key"]
        for tag in result["tags"]:
            for key, value in params.items():
                assert [key, value] in tag["components"]
        questionnaire_responses = result["questionnaire_responses"][
            f"spine_{device['device_name']}/1"
        ]
        iter_items = iter(questionnaire_responses.items())
        iter_key, iter_value = next(iter_items)
        filter_count = 0
        for answer in iter_value["answers"]:
            for key, value in params.items():
                if key in answer:
                    filter_count = filter_count + 1
                    assert value in answer[key]

        assert filter_count == len(params)


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
