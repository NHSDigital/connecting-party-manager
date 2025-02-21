import json
import os
from unittest import mock

import pytest
from domain.core.cpm_system_id import ProductId
from domain.core.root import Root
from domain.repository.epr_product_repository import EprProductRepository
from domain.repository.product_team_epr_repository import ProductTeamRepository
from event.json import json_loads

from conftest import dynamodb_client_with_sleep
from test_helpers.response_assertions import _response_assertions
from test_helpers.sample_data import CPM_PRODUCT_TEAM_NO_ID
from test_helpers.terraform import read_terraform_output
from test_helpers.validate_search_response import validate_product_result_body

TABLE_NAME = "hiya"


def _create_org():
    org = Root.create_ods_organisation(ods_code=CPM_PRODUCT_TEAM_NO_ID["ods_code"])
    product_team = org.create_product_team_epr(
        name=CPM_PRODUCT_TEAM_NO_ID["name"], keys=CPM_PRODUCT_TEAM_NO_ID["keys"]
    )
    return product_team


def _create_product(product, product_team):
    generated_product_id = ProductId.create()
    product_id = generated_product_id.id
    cpmproduct = product_team.create_epr_product(
        product_id=product_id, name=product["name"]
    )

    return cpmproduct


@pytest.mark.parametrize(
    "version",
    [
        "1",
    ],
)
@pytest.mark.integration
def test_no_results(version):
    product_team = _create_org()
    product_team_id = product_team.id
    params = {"product_team_id": product_team_id}
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client_with_sleep()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchEprProduct.index import cache as product_cache
        from api.searchEprProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client

        pt_repo = ProductTeamRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        pt_repo.write(entity=product_team)

        result = product_handler(
            event={
                "headers": {"version": version},
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
    "version,product",
    [
        ("1", {"name": "product-name-a"}),
        ("1", {"name": "product-name-b"}),
        ("1", {"name": "product-name-c"}),
        ("1", {"name": "product-name-d"}),
    ],
)
def test_index(version, product):
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client_with_sleep()
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
        from api.searchEprProduct.index import cache as product_cache
        from api.searchEprProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client
        product_repo = EprProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        product_repo.write(entity=cpmproduct)

        result = product_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    expected_result = json.dumps({"results": [cpmproduct.state()]})

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
    params = {"product_team_id": "123456"}
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client_with_sleep()

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchEprProduct.index import cache as product_cache
        from api.searchEprProduct.index import handler as product_handler

        product_cache["DYNAMODB_CLIENT"] = client

        EprProductRepository(
            table_name=product_cache["DYNAMODB_TABLE"],
            dynamodb_client=product_cache["DYNAMODB_CLIENT"],
        )

        result = product_handler(
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
    version = 1
    table_name = read_terraform_output("dynamodb_epr_table_name.value")
    client = dynamodb_client_with_sleep()

    product_team = _create_org()
    pt_repo = ProductTeamRepository(
        table_name=table_name,
        dynamodb_client=client,
    )
    pt_repo.write(entity=product_team)
    params = {"product_team_id": product_team.id}
    epr_products = []
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
            from api.searchEprProduct.index import cache as product_cache

            product_cache["DYNAMODB_CLIENT"] = client
            product_repo = EprProductRepository(
                table_name=product_cache["DYNAMODB_TABLE"],
                dynamodb_client=product_cache["DYNAMODB_CLIENT"],
            )

            product_repo.write(entity=cpmproduct)
        epr_products.append(cpmproduct)

    with mock.patch.dict(
        os.environ,
        {
            "DYNAMODB_TABLE": table_name,
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
        clear=True,
    ):
        from api.searchEprProduct.index import handler as product_handler

        result = product_handler(
            event={
                "headers": {"version": version},
                "pathParameters": params,
            }
        )

    assert result["statusCode"] == 200
    result_body = json_loads(result["body"])
    assert "results" in result_body
    assert isinstance(result_body["results"], list)
    validate_product_result_body(
        result_body["results"], [epr_product.state() for epr_product in epr_products]
    )
