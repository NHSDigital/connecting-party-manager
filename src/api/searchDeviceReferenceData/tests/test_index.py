import json
import os
from unittest import mock

import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.enum import Environment
from domain.core.root import Root
from domain.repository.cpm_product_repository import CpmProductRepository
from domain.repository.device_reference_data_repository import (
    DeviceReferenceDataRepository,
)
from domain.repository.product_team_epr_repository import ProductTeamRepository
from event.json import json_loads

from conftest import dynamodb_client_with_sleep as dynamodb_client
from test_helpers.response_assertions import _response_assertions
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.terraform import read_terraform_output
from test_helpers.validate_search_response import validate_product_result_body

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    return product_team


def _create_product(product, product_team):
    generated_product_id = ProductId.create()
    cpmproduct = product_team.create_cpm_product(
        product_id=generated_product_id.id, name=product["name"]
    )

    return cpmproduct


def _create_device_ref_data(device_ref_data, product):
    drd = product.create_device_reference_data(
        name=device_ref_data["name"], environment=Environment.DEV
    )

    return drd


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
@pytest.mark.integration
def test_no_results(version):
    product_team = _create_org()
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchDeviceReferenceData.index import cache as drd_cache
        from api.searchDeviceReferenceData.index import handler as drd_handler

        drd_cache["DYNAMODB_CLIENT"] = client

        pt_repo = ProductTeamRepository(
            table_name=drd_cache["DYNAMODB_TABLE"],
            dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
        )

        pt_repo.write(entity=product_team)
        product = _create_product(
            product={"name": "product-a"}, product_team=product_team
        )

        p_repo = CpmProductRepository(
            table_name=drd_cache["DYNAMODB_TABLE"],
            dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
        )

        p_repo.write(entity=product)
        product_state = product.state()
        params = {
            "product_team_id": product_team.id,
            "product_id": product_state["id"],
            "environment": Environment.DEV,
        }
        result = drd_handler(
            event={
                "headers": {"version": 1},
                "pathParameters": params,
            }
        )
    expected_result = json.dumps({"results": []})
    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "version,device_ref_data",
    [
        ("1", {"name": "device-ref-data-name-a"}),
        ("1", {"name": "device-ref-data-name-b"}),
        ("1", {"name": "device-ref-data-name-c"}),
        ("1", {"name": "device-ref-data-name-d"}),
    ],
)
def test_index(version, device_ref_data):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client()
    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)
    cpmproduct = _create_product(
        product={"name": "product-a"}, product_team=product_team
    )
    p_repo = CpmProductRepository(table_name=table_name, dynamodb_client=client)
    p_repo.write(entity=cpmproduct)
    product_state = cpmproduct.state()
    drd = _create_device_ref_data(device_ref_data=device_ref_data, product=cpmproduct)

    params = {
        "product_team_id": product_team.id,
        "product_id": product_state["id"],
        "environment": Environment.DEV,
    }
    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchDeviceReferenceData.index import cache as drd_cache
        from api.searchDeviceReferenceData.index import handler as drd_handler

        drd_cache["DYNAMODB_CLIENT"] = client
        drd_repo = DeviceReferenceDataRepository(
            table_name=drd_cache["DYNAMODB_TABLE"],
            dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
        )

        drd_repo.write(entity=drd)

        result = drd_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    expected_result = json.dumps({"results": [drd.state()]})

    expected = {
        "statusCode": 200,
        "body": expected_result,
        "headers": {
            "Content-Length": str(len(expected_result)),
            "Content-Type": "application/json",
            "Version": version,
        },
    }
    _response_assertions(
        result=result, expected=expected, check_body=True, check_content_length=True
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product_team(version):
    params = {
        "product_team_id": "123456",
        "product_id": "P.123-321",
        "environment": Environment.DEV,
    }
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchDeviceReferenceData.index import cache as drd_cache
        from api.searchDeviceReferenceData.index import handler as drd_handler

        drd_cache["DYNAMODB_CLIENT"] = client

        DeviceReferenceDataRepository(
            table_name=drd_cache["DYNAMODB_TABLE"],
            dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
        )

        result = drd_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 404
    assert result_body == {
        "errors": [
            {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Could not find ProductTeam for key ('123456')",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
def test_index_no_such_product(version):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client()

    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)

    params = {
        "product_team_id": product_team.id,
        "product_id": "P.123-321",
        "environment": Environment.DEV,
    }

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchDeviceReferenceData.index import cache as drd_cache
        from api.searchDeviceReferenceData.index import handler as drd_handler

        drd_cache["DYNAMODB_CLIENT"] = client

        DeviceReferenceDataRepository(
            table_name=drd_cache["DYNAMODB_TABLE"],
            dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
        )

        result = drd_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    result_body = json_loads(result["body"])

    assert result["statusCode"] == 404
    assert result_body == {
        "errors": [
            {
                "code": "RESOURCE_NOT_FOUND",
                "message": f"Could not find CpmProduct for key ('{product_team.id}', 'P.123-321')",
            }
        ]
    }


@pytest.mark.integration
@pytest.mark.parametrize(
    "device_ref_data",
    [
        [
            {"name": "device-ref-data-name-a"},
            {"name": "device-ref-data-name-b"},
            {"name": "device-ref-data-name-c"},
            {"name": "device-ref-data-name-d"},
        ],
    ],
)
def test_index_multiple_returned(device_ref_data):
    version = 1
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client()

    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)
    cpmproduct = _create_product(
        product={"name": "product-a"}, product_team=product_team
    )
    p_repo = CpmProductRepository(table_name=table_name, dynamodb_client=client)
    p_repo.write(entity=cpmproduct)
    product_state = cpmproduct.state()
    params = {
        "product_team_id": product_team.id,
        "product_id": product_state["id"],
        "environment": Environment.DEV,
    }
    drds = []
    for dev_ref_dat in device_ref_data:
        drd = _create_device_ref_data(device_ref_data=dev_ref_dat, product=cpmproduct)
        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchDeviceReferenceData.index import cache as drd_cache

            drd_cache["DYNAMODB_CLIENT"] = client
            drd_repo = DeviceReferenceDataRepository(
                table_name=drd_cache["DYNAMODB_TABLE"],
                dynamodb_client=drd_cache["DYNAMODB_CLIENT"],
            )

            drd_repo.write(entity=drd)
        drds.append(drd)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchDeviceReferenceData.index import handler as drd_handler

        result = drd_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    assert result["statusCode"] == 200
    result_body = json_loads(result["body"])
    assert "results" in result_body
    assert isinstance(result_body["results"], list)
    validate_product_result_body(result_body["results"], [d.state() for d in drds])
