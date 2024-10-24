import os
from unittest import mock

import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.root.v3 import Root
from domain.repository.cpm_product_repository.v3 import CpmProductRepository
from domain.repository.product_team_repository.v2 import ProductTeamRepository
from event.aws.client import dynamodb_client
from event.json import json_loads

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
    product_id = generated_product_id.id
    cpmproduct = product_team.create_cpm_product(
        product_id=product_id, name=product["name"]
    )

    return cpmproduct


@pytest.mark.integration
def test_no_results():
    product_team = _create_org()
    product_team_id = product_team.id
    params = {"product_team_id": product_team_id}
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
        from api.searchCpmProduct.index import cache as product_cache
        from api.searchCpmProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client

        pt_repo = ProductTeamRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        pt_repo.write(entity=product_team)

        result = product_handler(
            event={
                "headers": {"version": 1},
                "pathParameters": params,
            }
        )
    result_body = json_loads(result["body"])
    assert result["statusCode"] == 200
    assert len(result_body) == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    "product",
    [
        {"name": "product-name-a"},
        {"name": "product-name-b"},
        {"name": "product-name-c"},
        {"name": "product-name-d"},
    ],
)
def test_index(product):
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()
    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)
    cpmproduct = _create_product(product=product, product_team=product_team)
    params = {"product_team_id": product_team.id}

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchCpmProduct.index import cache as product_cache
        from api.searchCpmProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        product_repo.write(entity=cpmproduct)

        result = product_handler(
            event={
                "headers": {"version": 1},
                "pathParameters": params,
            }
        )

    assert result["statusCode"] == 200

    result_body = json_loads(result["body"])
    assert isinstance(result_body, list)
    validate_product_result_body(result_body, cpmproduct.state())


@pytest.mark.integration
def test_index_no_such_product_team():
    params = {"product_team_id": "123456"}
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
        from api.searchCpmProduct.index import cache as product_cache
        from api.searchCpmProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client

        CpmProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        result = product_handler(
            event={
                "headers": {"version": 1},
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
    "products",
    [
        [
            {"name": "product-name-a"},
            {"name": "product-name-b"},
            {"name": "product-name-c"},
            {"name": "product-name-d"},
        ],
    ],
)
def test_index_multiple_returned(products):
    table_name = read_terraform_output("dynamodb_table_name.value")
    client = dynamodb_client()

    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)
    params = {"product_team_id": product_team.id}
    cpm_products = []
    for product in products:
        cpmproduct = _create_product(product=product, product_team=product_team)
        with mock.patch.dict(
            os.environ,
            {
                "DYNAMODB_TABLE": table_name,
                "AWS_DEFAULT_REGION": "eu-west-2",
            },
            clear=True,
        ):
            from api.searchCpmProduct.index import cache as product_cache

            product_cache["DYNAMODB_CLIENT"] = client
            product_repo = CpmProductRepository(
                table_name=product_cache["DYNAMODB_TABLE"],
                dynamodb_client=product_cache["DYNAMODB_CLIENT"],
            )

            product_repo.write(entity=cpmproduct)
        cpm_products.append(cpmproduct)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchCpmProduct.index import handler as product_handler

        result = product_handler(
            event={
                "headers": {"version": 1},
                "pathParameters": params,
            }
        )

    assert result["statusCode"] == 200

    result_body = json_loads(result["body"])
    assert isinstance(result_body, list)
    validate_product_result_body(
        result_body, [cpm_product.state() for cpm_product in cpm_products]
    )
