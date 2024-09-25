import os
from unittest import mock

import pytest
from domain.core.device.v2 import Device
from domain.core.device.v2 import DeviceType as DeviceTypeV2
from domain.core.product_team.v2 import ProductTeam
from domain.core.questionnaire.v2 import Questionnaire
from domain.core.root.v2 import Root
from domain.repository.device_repository.v2 import DeviceRepository
from event.aws.client import dynamodb_client
from event.json import json_loads

from test_helpers.dynamodb import mock_table
from test_helpers.terraform import read_terraform_output
from test_helpers.uuid import consistent_uuid
from test_helpers.validate_search_response import validate_result_body

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code="ABC")
    product_team = org.create_product_team(
        id=consistent_uuid(1), name="product-team-name-a"
    )
    return product_team


def _create_device(device: Device, product_team: ProductTeam, params: dict):
    cpm_device = product_team.create_device(
        name=device["device_name"], device_type=DeviceTypeV2.ENDPOINT
    )
    questionnaire = Questionnaire(name=f"spine_{device['device_name']}", version=1)

    response = []
    for key, value in params.items():
        questionnaire.add_question(name=key, answer_types=(str,), mandatory=True)
        response.append({key: [value]})

    questionnaire_response = questionnaire.respond(responses=response)
    cpm_device.add_questionnaire_response(questionnaire_response=questionnaire_response)
    tag_params = [params]
    cpm_device.add_tags(tags=tag_params)
    return cpm_device


@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "nhs_id_code": "5NR",
            "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
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
        from api.searchSdsEndpoint.index import cache as endpoint_cache
        from api.searchSdsEndpoint.index import handler as endpoint_handler

        endpoint_cache["DYNAMODB_CLIENT"] = client

        DeviceRepository(
            table_name=endpoint_cache["DYNAMODB_TABLE"],
            dynamodb_client=endpoint_cache["DYNAMODB_CLIENT"],
        )

        result = endpoint_handler(
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
                "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_party_key": "foo",
            },
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
        (
            {"nhs_id_code": "5NR", "nhs_mhs_party_key": "foo"},
            {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
        ),
    ],
)
def test_index(params, device):
    product_team = _create_org()
    cpm_device = _create_device(device=device, product_team=product_team, params=params)

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
        from api.searchSdsEndpoint.index import cache as endpoint_cache
        from api.searchSdsEndpoint.index import handler as endpoint_handler

        endpoint_cache["DYNAMODB_CLIENT"] = client

        endpoint_repo = DeviceRepository(
            table_name=endpoint_cache["DYNAMODB_TABLE"],
            dynamodb_client=endpoint_cache["DYNAMODB_CLIENT"],
        )
        endpoint_repo.write(cpm_device)

        result = endpoint_handler(
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
                "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
        (
            {
                "nhs_id_code": "5NR",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
                "nhs_mhs_party_key": "foo",
            },
            [
                {"device_key": "P.AAA-CCC", "device_name": "device-name-a"},
                {"device_key": "P.AAA-HHH", "device_name": "device-name-b"},
            ],
        ),
        (
            {"nhs_id_code": "5NR", "nhs_mhs_party_key": "foo"},
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
        cpm_device = _create_device(
            device=device, product_team=product_team, params=params
        )

        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchSdsEndpoint.index import cache as endpoint_cache

            endpoint_cache["DYNAMODB_CLIENT"] = client
            endpoint_repo = DeviceRepository(
                table_name=endpoint_cache["DYNAMODB_TABLE"],
                dynamodb_client=endpoint_cache["DYNAMODB_CLIENT"],
            )
            endpoint_repo.write(cpm_device)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsEndpoint.index import handler as endpoint_handler

        result = endpoint_handler(
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
    ["params", "error_code", "error_msg", "status_code"],
    [
        (
            {
                "nhs_id_code": "RTX",
            },
            "VALIDATION_ERROR",
            "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key",
            400,
        ),
        (
            {"nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08"},
            "VALIDATION_ERROR",
            "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key",
            400,
        ),
        (
            {"nhs_mhs_party_key": "D81631-827817"},
            "VALIDATION_ERROR",
            "At least 2 query parameters should be provided of type, nhs_id_code, nhs_mhs_svc_ia and nhs_mhs_party_key",
            400,
        ),
        (
            {
                "nhs_id_code": "RTX",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:ebs:PRSC_IN040000UK08",
                "foo": "bar",
            },
            "VALIDATION_ERROR",
            "extra fields not permitted",
            400,
        ),
    ],
)
def test_filter_errors(params, error_code, error_msg, status_code):
    with mock_table(TABLE_NAME) as client, mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": TABLE_NAME,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsEndpoint.index import cache, handler

        cache["DYNAMODB_CLIENT"] = client
        result = handler(
            event={
                "headers": {"version": 1},
                "queryStringParameters": params,
                "multiValueHeaders": {"Host": ["foo.co.uk"]},
            }
        )
    assert result["statusCode"] == status_code
    result_body = json_loads(result["body"])

    assert result_body["issue"][0]["details"]["coding"][0]["code"] == error_code
    assert result_body["issue"][0]["diagnostics"] == error_msg


@pytest.mark.integration
@pytest.mark.parametrize(
    "params, devices",
    [
        (
            {
                "nhs_id_code": "5NR",
                "nhs_mhs_svc_ia": "urn:nhs:names:services:mm:PORX_IN090101UK31",
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
        cpm_device = _create_device(
            device=device, product_team=product_team, params=params
        )

        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchSdsEndpoint.index import cache as endpoint_cache

            endpoint_cache["DYNAMODB_CLIENT"] = client
            endpoint_repo = DeviceRepository(
                table_name=endpoint_cache["DYNAMODB_TABLE"],
                dynamodb_client=endpoint_cache["DYNAMODB_CLIENT"],
            )
            endpoint_repo.write(cpm_device)

            # Soft delete the first device
            if index == 0:
                inactive_device = endpoint_repo.read(cpm_device.id)
                inactive_device.delete()
                endpoint_repo.write(inactive_device)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchSdsEndpoint.index import handler as endpoint_handler

        result = endpoint_handler(
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
