import os
from unittest import mock

import pytest
from domain.core.device import Device
from domain.core.device_key import DeviceKeyType
from domain.core.product_team import ProductTeam
from domain.core.questionnaire import Questionnaire
from domain.core.root import Root
from domain.repository.device_repository import DeviceRepository
from event.aws.client import dynamodb_client
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output
from test_helpers.validate_search_response import validate_result_body

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(name="product-team-name-a")
    return product_team


def _create_device(
    device_data: dict, product_team: ProductTeam, questionnaire_data: dict[str, str]
) -> Device:
    product = product_team.create_cpm_product(name="my-product")

    device = product.create_device(name=device_data["device_name"])
    device.add_key(
        key_value=device_data["device_key"], key_type=DeviceKeyType.PRODUCT_ID
    )

    questionnaire = Questionnaire(name=f"spine_{device_data['device_name']}", version=1)

    questionnaire_response = questionnaire.respond(responses=response)
    device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    tag_params = [questionnaire_data]
    device.add_tags(tags=tag_params)
    return device


@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "nhs_id_code": "5NR",
            "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
        },
    ],
)
def test_no_results(params):
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

        DeviceRepository(
            table_name=device_cache["DYNAMODB_TABLE"],
            dynamodb_client=device_cache["DYNAMODB_CLIENT"],
        )

        result = device_handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    result_body = json_loads(result["body"])

    assert result["statusCode"] == 200
    assert len(result_body) == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "params, device",
    [
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_manufacturer_org": "foo",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_party_key": "foo",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_manufacturer_org": "foo",
                "nhs_mhs_party_key": "foo",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
    ],
)
def test_index(params, device):
    product_team = _create_org()
    cpmdevice = _create_device(
        device_data=device, product_team=product_team, questionnaire_data=params
    )

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
    assert result["statusCode"] == 200

    result_body = json_loads(result["body"])
    validate_result_body(result_body, device, params)


@pytest.mark.integration
@pytest.mark.parametrize(
    "params, devices",
    [
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_manufacturer_org": "foo",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_party_key": "foo",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_manufacturer_org": "foo",
                "nhs_mhs_party_key": "foo",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
    ],
)
def test_multiple_returned(params, devices):
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()

    product_team = _create_org()
    for device in devices:
        cpmdevice = _create_device(
            device_data=device, product_team=product_team, questionnaire_data=params
        )

        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchSdsDevice.index import cache as device_cache

            device_cache["DYNAMODB_CLIENT"] = client
            device_repo = DeviceRepository(
                table_name=device_cache["DYNAMODB_TABLE"],
                dynamodb_client=device_cache["DYNAMODB_CLIENT"],
            )
            device_repo.write(cpmdevice)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsDevice.index import handler as device_handler

        result = device_handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    assert result["statusCode"] == 200

    result_body = json_loads(result["body"])
    devices.reverse()
    if result_body[0]["name"] != devices[0]["device_name"]:
        devices.reverse()
    validate_result_body(result_body, devices, params)


@pytest.mark.parametrize(
    "params, error, status_code",
    [
        ({"nhs_id_code": "5NR"}, "MISSING_VALUE", 400),
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
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:oasis:names:tc:ebxml-msg:service:Acknowledgment",
                "foo": "bar",
            },
            "VALIDATION_ERROR",
            400,
        ),
    ],
)
def test_filter_errors(params, error, status_code):
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
    assert result["statusCode"] == status_code
    assert error in result["body"]


@pytest.mark.integration
@pytest.mark.parametrize(
    "params, devices",
    [
        (
            {
                "nhs_id_code": "5NR",
                "nhs_as_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
    ],
)
def test_only_active_returned(params, devices):
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()

    product_team = _create_org()
    for index, device in enumerate(devices):
        cpmdevice = _create_device(
            device_data=device, product_team=product_team, questionnaire_data=params
        )

        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchSdsDevice.index import cache as device_cache

            device_cache["DYNAMODB_CLIENT"] = client
            device_repo = DeviceRepository(
                table_name=device_cache["DYNAMODB_TABLE"],
                dynamodb_client=device_cache["DYNAMODB_CLIENT"],
            )
            device_repo.write(cpmdevice)

            # Soft delete the first device
            if index == 0:
                inactive_device = device_repo.read(cpmdevice.id)
                inactive_device.delete()
                device_repo.write(inactive_device)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsDevice.index import handler as device_handler

        result = device_handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )

    result_body = json_loads(result["body"])
    assert len(result_body) == 1

    assert result["statusCode"] == 200

    for index, result in enumerate(result_body):
        assert result["status"] == "active"
        assert result["name"] == "device-name-b"
